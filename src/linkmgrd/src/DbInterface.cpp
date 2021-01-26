/*
 * DbInterface.cpp
 *
 *  Created on: Oct 23, 2020
 *      Author: tamer
 */

#include <algorithm>
#include <tuple>

#include <boost/algorithm/string.hpp>
#include <boost/bind/bind.hpp>
#include <boost/lexical_cast.hpp>

#include "swss/netdispatcher.h"
#include "swss/netlink.h"
#include "swss/select.h"

#include "DbInterface.h"
#include "MuxManager.h"
#include "common/MuxLogger.h"
#include "common/MuxException.h"
#include "NetMsgInterface.h"

namespace mux
{
constexpr auto DEFAULT_TIMEOUT_MSEC = 1000;
std::vector<std::string> DbInterface::mMuxState = {"active", "standby", "unknown"};

//
// ---> DbInterface(mux::MuxManager *muxManager);
//
// class constructor
//
DbInterface::DbInterface(mux::MuxManager *muxManager, boost::asio::io_service *ioService) :
    mMuxManagerPtr(muxManager),
    mStrand(*ioService)
{
}


//
// ---> getMuxState(const std::string &portName);
//
// retrieve the current MUX state
//
void DbInterface::getMuxState(const std::string &portName)
{
    MUXLOGDEBUG(portName);

    boost::asio::io_service &ioService = mStrand.context();
    ioService.post(mStrand.wrap(boost::bind(
        &DbInterface::handleGetMuxState,
        this,
        portName
    )));
}

//
// ---> setMuxState(const std::string &portName, mux_state::MuxState::Label label);
//
// set MUX state in APP DB for orchagent processing
//
void DbInterface::setMuxState(const std::string &portName, mux_state::MuxState::Label label)
{
    MUXLOGINFO(boost::format("%s: setting mux to %s") % portName % mMuxState[label]);

    boost::asio::io_service &ioService = mStrand.context();
    ioService.post(mStrand.wrap(boost::bind(
        &DbInterface::handleSetMuxState,
        this,
        portName,
        label
    )));
}

//
// ---> probeMuxState(const std::string &portName)
//
// trigger xcvrd to read MUX state using i2c
//
void DbInterface::probeMuxState(const std::string &portName)
{
    MUXLOGINFO(portName);

    boost::asio::io_service &ioService = mStrand.context();
    ioService.post(mStrand.wrap(boost::bind(
        &DbInterface::handleProbeMuxState,
        this,
        portName
    )));
}

//
// ---> initialize();
//
// initialize DB tables and start SWSS listening thread
//
void DbInterface::initialize()
{
    try {
        mAppDbPtr = std::make_shared<swss::DBConnector> ("APPL_DB", 0);
        mStateDbPtr = std::make_shared<swss::DBConnector> ("STATE_DB", 0);

        mAppDbMuxTablePtr = std::make_shared<swss::ProducerStateTable> (
            mAppDbPtr.get(), APP_MUX_CABLE_TABLE_NAME
        );
        mAppDbMuxCommandTablePtr = std::make_shared<swss::Table> (
            mAppDbPtr.get(), APP_MUX_CABLE_COMMAND_TABLE_NAME
        );
        mStateDbMuxTablePtr = std::make_shared<swss::ProducerStateTable> (
            mStateDbPtr.get(), STATE_MUX_CABLE_TABLE_NAME
        );
        mMuxStateTablePtr = std::make_shared<swss::Table> (mStateDbPtr.get(), STATE_MUX_CABLE_TABLE_NAME);

        mSwssThreadPtr = std::make_shared<boost::thread> (&DbInterface::handleSwssNotification, this);
    }
    catch (const std::bad_alloc& ex) {
        std::ostringstream errMsg;
        errMsg << "Failed allocate memory. Exception details: " << ex.what();

        throw MUX_ERROR(BadAlloc, errMsg.str());
    }
}

//
// ---> updateServerMacAddress(boost::asio::ip::address serverIp, uint8_t *serverMac);
//
// Update Server MAC address behind a MUX port
//
void DbInterface::updateServerMacAddress(boost::asio::ip::address serverIp, const uint8_t *serverMac)
{
    MUXLOGDEBUG(boost::format("server IP: %s") % serverIp.to_string());

    ServerIpPortMap::const_iterator cit = mServerIpPortMap.find(serverIp);
    if (cit != mServerIpPortMap.cend()) {
        std::array<uint8_t, ETHER_ADDR_LEN> macAddress;

        memcpy(macAddress.data(), serverMac, macAddress.size());

        mMuxManagerPtr->processGetServerMacAddress(cit->second, macAddress);
    }
}

//
// ---> handleGetMuxState(const std::string portName);
//
// get state db MUX state
//
void DbInterface::handleGetMuxState(const std::string portName)
{
    MUXLOGDEBUG(portName);

    std::string state;
    if (mMuxStateTablePtr->hget(portName, "state", state)) {
        mMuxManagerPtr->processGetMuxState(portName, state);
    }
}

//
// ---> handleSetMuxState(const std::string portName, mux_state::MuxState::Label label);
//
// set MUX state in APP DB for orchagent processing
//
void DbInterface::handleSetMuxState(const std::string portName, mux_state::MuxState::Label label)
{
    MUXLOGINFO(boost::format("%s: setting mux state to %s") % portName % mMuxState[label]);

    if (label <= mux_state::MuxState::Unknown) {
        std::vector<swss::FieldValueTuple> values = {
            {"state", mMuxState[label]},
        };
        mAppDbMuxTablePtr->set(portName, values);
    }
}

//
// ---> handleProbeMuxState(const std::string portName)
//
// trigger xcvrd to read MUX state using i2c
//
void DbInterface::handleProbeMuxState(const std::string portName)
{
    MUXLOGINFO(portName);

    mAppDbMuxCommandTablePtr->hset(portName, "command", "probe");
}

//
// ---> getLoopback2InterfaceInfo(
//          std::shared_ptr<swss::DBConnector> configDbConnector,
//          std::shared_ptr<swss::DBConnector> stateDbConnector
//      );
//
// retrieve Loopback2 interface information and block until it shows as OK in the state db
//
void DbInterface::getLoopback2InterfaceInfo(
    std::shared_ptr<swss::DBConnector> configDbConnector,
    std::shared_ptr<swss::DBConnector> stateDbConnector
)
{
    MUXLOGINFO("Reading Loopback2 interface information");
    std::string loopback2 = "Loopback2|";
    swss::Table configDbLoopbackTable(configDbConnector.get(), CFG_LOOPBACK_INTERFACE_TABLE_NAME);
    swss::Table stateDbInterfaceTable(stateDbConnector.get(), STATE_INTERFACE_TABLE_NAME);
    std::string loopback2IntfKey;
    std::vector<std::string> loopbackIntfs;
    configDbLoopbackTable.getKeys(loopbackIntfs);
    for (auto &loopbackIntf: loopbackIntfs) {
        size_t pos = loopbackIntf.find(loopback2);
        if (pos != std::string::npos) {
            std::string ip = loopbackIntf.substr(loopback2.size(), loopbackIntf.size() - loopback2.size());
            MUXLOGINFO(boost::format("configDb Loopback2: ip: %s") % ip);

            pos = ip.find("/");
            if (pos != std::string::npos) {
                ip.erase(pos);
            }
            boost::system::error_code errorCode;
            boost::asio::ip::address ipAddress = boost::asio::ip::make_address(ip, errorCode);
            if (!errorCode) {
                if (ipAddress.is_v4()) {
                    mMuxManagerPtr->setLoopbackIpv4Address(ipAddress);
                    loopback2IntfKey = loopbackIntf;
                }
                else if (ipAddress.is_v6()) {
                    // handle IPv6 probing
                }
            } else {
                MUXLOGFATAL(boost::format("Received Loopback2 IP: %s, error code: %d") % ip % errorCode);
            }
        }
    }

    while (true) {
        std::vector<swss::FieldValueTuple> fieldValues;
        stateDbInterfaceTable.get(loopback2IntfKey, fieldValues);
        std::vector<swss::FieldValueTuple>::const_iterator cit = std::find_if(
            fieldValues.cbegin(),
            fieldValues.cend(),
            [] (const swss::FieldValueTuple &fv) {return fvField(fv) == "state";}
        );
        if (cit != fieldValues.cend()) {
            const std::string f = cit->first;
            const std::string v = cit->second;

            MUXLOGINFO(boost::format("key: %s: f: %s, v: %s") % loopback2IntfKey % f % v);
            if (v == "ok") {
                break;
            }

            boost::this_thread::sleep(boost::posix_time::milliseconds(DEFAULT_TIMEOUT_MSEC));
        }
    }
}

//
// ---> getServerIpAddress(std::shared_ptr<swss::DBConnector> configDbConnector);
//
// retrieve server/blades IP address and builds a map of IP to port name
//
void DbInterface::getServerIpAddress(std::shared_ptr<swss::DBConnector> configDbConnector)
{
    MUXLOGINFO("Reading MUX Server IPs");
    swss::Table configDbMuxCableTable(configDbConnector.get(), CFG_MUX_CABLE_TABLE_NAME);
    std::vector<swss::KeyOpFieldsValuesTuple> entries;

    configDbMuxCableTable.getContent(entries);
    for (auto &entry: entries) {
        std::string portName = kfvKey(entry);
        std::string operation = kfvOp(entry);
        std::vector<swss::FieldValueTuple> fieldValues = kfvFieldsValues(entry);

        std::vector<swss::FieldValueTuple>::const_iterator cit = std::find_if(
            fieldValues.cbegin(),
            fieldValues.cend(),
            [] (const swss::FieldValueTuple &fv) {return fvField(fv) == "server_ipv4";}
        );
        if (cit != fieldValues.cend()) {
            const std::string f = cit->first;
            std::string smartNicIpAddress = cit->second;

            MUXLOGDEBUG(boost::format("port: %s, %s = %s") % portName % f % smartNicIpAddress);

            size_t pos = smartNicIpAddress.find("/");
            if (pos != std::string::npos) {
                smartNicIpAddress.erase(pos);
            }

            boost::system::error_code errorCode;
            boost::asio::ip::address ipAddress = boost::asio::ip::make_address(smartNicIpAddress, errorCode);
            if (!errorCode) {
                mMuxManagerPtr->addOrUpdateMuxPort(portName, ipAddress);
                mServerIpPortMap[ipAddress] = portName;
            } else {
                MUXLOGFATAL(boost::format("%s: Received invalid server IP: %s, error code: %d") %
                    portName %
                    smartNicIpAddress %
                    errorCode
                );
            }
        }
    }
}

//
// ---> handleMuxPortConfigNotifiction(swss::SubscriberStateTable &configMuxTable);
//
// handles MUX port configuration change notification
//
void DbInterface::handleMuxPortConfigNotifiction(swss::SubscriberStateTable &configMuxTable)
{
    std::deque<swss::KeyOpFieldsValuesTuple> entries;

    configMuxTable.pops(entries);
    for (auto &entry: entries) {
        std::string port = kfvKey(entry);
        std::string operation = kfvOp(entry);
        std::vector<swss::FieldValueTuple> fieldValues = kfvFieldsValues(entry);

        std::vector<swss::FieldValueTuple>::const_iterator cit = std::find_if(
            fieldValues.cbegin(),
            fieldValues.cend(),
            [] (const swss::FieldValueTuple &fv) {return fvField(fv) == "state";}
        );
        if (cit != fieldValues.cend()) {
            const std::string f = cit->first;
            const std::string v = cit->second;

            MUXLOGDEBUG(boost::format("key: %s, Operation: %s, f: %s, v: %s") %
                port %
                operation %
                f %
                v
            );
            mMuxManagerPtr->updateMuxPortConfig(port, v);
        }
    }
}

//
// ---> handleLocalhostConfigNotifiction(swss::SubscriberStateTable &configLocalhostTable);
//
// handles localhost configuration change notification
//
void DbInterface::handleLocalhostConfigNotifiction(swss::SubscriberStateTable &configLocalhostTable)
{
    std::deque<swss::KeyOpFieldsValuesTuple> entries;

    configLocalhostTable.pops(entries);
    for (auto &entry: entries) {
        std::string key = kfvKey(entry);
        if (key == "LINK_PROBE") {
            std::string operation = kfvOp(entry);
            std::vector<swss::FieldValueTuple> fieldValues = kfvFieldsValues(entry);

            for (auto &fieldValue: fieldValues) {
                std::string f = fvField(fieldValue);
                std::string v = fvValue(fieldValue);
                if (f == "interval") {
                    mMuxManagerPtr->setTimeoutIpv4_msec(boost::lexical_cast<uint32_t> (v));
                } else if (f == "interval_for_v6") {
                    mMuxManagerPtr->setTimeoutIpv6_msec(boost::lexical_cast<uint32_t> (v));
                } else if (f == "timeout") {
                    mMuxManagerPtr->setStateChangeRetryCount(boost::lexical_cast<uint32_t> (v));
                } else if (f == "suspend_timer") {
                    mMuxManagerPtr->setSuspendTimeout_msec(boost::lexical_cast<uint32_t> (v));
                }

                MUXLOGINFO(boost::format("key: %s, Operation: %s, f: %s, v: %s") %
                    key %
                    operation %
                    f %
                    v
                );
            }
        }
    }
}

//
// ---> handleLinkStateNotifiction(swss::SubscriberStateTable &appdbPortTable);
//
// handles link state change notification
//
void DbInterface::handleLinkStateNotifiction(swss::SubscriberStateTable &appdbPortTable)
{
    std::deque<swss::KeyOpFieldsValuesTuple> entries;

    appdbPortTable.pops(entries);
    for (auto &entry: entries) {
        std::string port = kfvKey(entry);
        std::string operation = kfvOp(entry);
        std::vector<swss::FieldValueTuple> fieldValues = kfvFieldsValues(entry);

        std::vector<swss::FieldValueTuple>::const_iterator cit = std::find_if(
            fieldValues.cbegin(),
            fieldValues.cend(),
            [] (const swss::FieldValueTuple &fv) {return fvField(fv) == "oper_status";}
        );
        if (cit != fieldValues.cend()) {
            const std::string f = cit->first;
            const std::string v = cit->second;

            MUXLOGDEBUG(boost::format("port: %s, operation: %s, f: %s, v: %s") %
                port %
                operation %
                f %
                v
            );
            mMuxManagerPtr->addOrUpdateMuxPortLinkState(port, v);
        }
    }
}

//
// ---> handleMuxResponseNotifiction(swss::SubscriberStateTable &appdbPortTable);
//
// handles MUX response (from xcvrd) notification
//
void DbInterface::handleMuxResponseNotifiction(swss::SubscriberStateTable &appdbPortTable)
{
    std::deque<swss::KeyOpFieldsValuesTuple> entries;

    appdbPortTable.pops(entries);
    for (auto &entry: entries) {
        std::string port = kfvKey(entry);
        std::string oprtation = kfvOp(entry);
        std::vector<swss::FieldValueTuple> fieldValues = kfvFieldsValues(entry);

        std::vector<swss::FieldValueTuple>::const_iterator cit = std::find_if(
            fieldValues.cbegin(),
            fieldValues.cend(),
            [] (const swss::FieldValueTuple &fv) {return fvField(fv) == "response";}
        );
        if (cit != fieldValues.cend()) {
            const std::string f = cit->first;
            const std::string v = cit->second;

            MUXLOGINFO(boost::format("port: %s, operation: %s, f: %s, v: %s") %
                port %
                oprtation %
                f %
                v
            );
//            swss::Table table(mAppDbPtr.get(), APP_MUX_CABLE_RESPONSE_TABLE_NAME);
//            table.hdel(port, "response");
            mMuxManagerPtr->processProbeMuxState(port, v);
        }
    }
}

//
// ---> handleMuxStateNotifiction(swss::SubscriberStateTable &statedbPortTable);
//
// statedbPortTable (in) reference to state db port table
//
void DbInterface::handleMuxStateNotifiction(swss::SubscriberStateTable &statedbPortTable)
{
    std::deque<swss::KeyOpFieldsValuesTuple> entries;

    statedbPortTable.pops(entries);
    for (auto &entry: entries) {
        std::string port = kfvKey(entry);
        std::string oprtation = kfvOp(entry);
        std::vector<swss::FieldValueTuple> fieldValues = kfvFieldsValues(entry);

        std::vector<swss::FieldValueTuple>::const_iterator cit = std::find_if(
            fieldValues.cbegin(),
            fieldValues.cend(),
            [] (const swss::FieldValueTuple &fv) {return fvField(fv) == "state";}
        );
        if (cit != fieldValues.cend()) {
            const std::string f = cit->first;
            const std::string v = cit->second;

            MUXLOGINFO(boost::format("port: %s, operation: %s, f: %s, v: %s") %
                port %
                oprtation %
                f %
                v
            );
            mMuxManagerPtr->addOrUpdateMuxPortMuxState(port, v);
        }
    }
}

//
// ---> handleSwssNotification();
//
// main thread method for handling SWSS notification
//
void DbInterface::handleSwssNotification()
{
    std::shared_ptr<swss::DBConnector> configDbPtr = std::make_shared<swss::DBConnector> ("CONFIG_DB", 0);
    std::shared_ptr<swss::DBConnector> appDbPtr = std::make_shared<swss::DBConnector> ("APPL_DB", 0);
    std::shared_ptr<swss::DBConnector> stateDbPtr = std::make_shared<swss::DBConnector> ("STATE_DB", 0);

    // For reading Link Prober configurations from the localhost table name
    swss::SubscriberStateTable configDbLocalhostTable(configDbPtr.get(), "LOCALHOST"/*CFG_LOCALHOST_TABLE_NAME*/);

    swss::SubscriberStateTable configDbMuxTable(configDbPtr.get(), CFG_MUX_CABLE_TABLE_NAME);

    // for link up/down, should be in state db down the road
    swss::SubscriberStateTable appDbPortTable(appDbPtr.get(), APP_PORT_TABLE_NAME);
    // for command responses from the driver
    swss::SubscriberStateTable appDbMuxResponseTable(appDbPtr.get(), APP_MUX_CABLE_RESPONSE_TABLE_NAME);
    // for getting state db MUX state when orchagent updates it
    swss::SubscriberStateTable stateDbPortTable(stateDbPtr.get(), STATE_MUX_CABLE_TABLE_NAME);

    getLoopback2InterfaceInfo(configDbPtr, stateDbPtr);
    getServerIpAddress(configDbPtr);

    NetMsgInterface netMsgInterface(*this);
    swss::NetDispatcher::getInstance().registerMessageHandler(RTM_NEWNEIGH, &netMsgInterface);
    swss::NetDispatcher::getInstance().registerMessageHandler(RTM_DELNEIGH, &netMsgInterface);

    swss::NetLink netlinkNeighbor;
    netlinkNeighbor.registerGroup(RTNLGRP_NEIGH);
    netlinkNeighbor.dumpRequest(RTM_GETNEIGH);

    swss::Select swssSelect;
    swssSelect.addSelectable(&configDbLocalhostTable);
    swssSelect.addSelectable(&configDbMuxTable);
    swssSelect.addSelectable(&appDbPortTable);
    swssSelect.addSelectable(&appDbMuxResponseTable);
    swssSelect.addSelectable(&stateDbPortTable);
    swssSelect.addSelectable(&netlinkNeighbor);

    while (mPollSwssNotifcation) {
        swss::Selectable *selectable;
        int ret = swssSelect.select(&selectable, DEFAULT_TIMEOUT_MSEC);

        if (ret == swss::Select::ERROR) {
            MUXLOGERROR("Error had been returned in select");
            continue;
        }
        else if (ret == swss::Select::TIMEOUT) {
            continue;
        }
        else if (ret != swss::Select::OBJECT) {
            MUXLOGERROR(boost::format("Unknown return value from Select: %d") % ret);
            continue;
        }

        if (selectable == static_cast<swss::Selectable *> (&configDbLocalhostTable)) {
            handleLocalhostConfigNotifiction(configDbLocalhostTable);
        }
        else if (selectable == static_cast<swss::Selectable *> (&configDbMuxTable)) {
            handleMuxPortConfigNotifiction(configDbMuxTable);
        }
        else if (selectable == static_cast<swss::Selectable *> (&appDbPortTable)) {
            handleLinkStateNotifiction(appDbPortTable);
        }
        else if (selectable == static_cast<swss::Selectable *> (&appDbMuxResponseTable)) {
            handleMuxResponseNotifiction(appDbMuxResponseTable);
        }
        else if (selectable == static_cast<swss::Selectable *> (&stateDbPortTable)) {
            handleMuxStateNotifiction(stateDbPortTable);
        }
        else if (selectable == static_cast<swss::Selectable *> (&netlinkNeighbor)) {
            continue;
        }
        else {
            MUXLOGERROR("Unknown object returned by select");
        }
    }

    mMuxManagerPtr->terminate();
}

} /* namespace common */

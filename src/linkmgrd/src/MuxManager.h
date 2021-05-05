/*
 * MuxManager.h
 *
 *  Created on: Oct 4, 2020
 *      Author: tamer
 */

#ifndef MUXMANAGER_H_
#define MUXMANAGER_H_

#include <map>
#include <memory>

#include <boost/asio.hpp>
#include <boost/asio/signal_set.hpp>

#include "MuxPort.h"
#include "common/MuxConfig.h"
#include "DbInterface.h"

namespace mux
{
using PortMap = std::map<std::string, std::shared_ptr<MuxPort>>;
using PortMapIterator = PortMap::iterator;

/**
 *@class MuxManager
 *
 *@brief host collection MuxPort object, each has MuxPort configuration, LinkManagerStateMachine.
 */
class MuxManager
{
public:
    /**
    *@method MuxManager
    *
    *@brief class default constructor
    */
    MuxManager();

    /**
    *@method MuxManager
    *
    *@brief class copy constructor
    *
    *@param MuxManager (in)  reference to MuxManager object to be copied
    */
    MuxManager(const MuxManager &) = delete;

    /**
    *@method ~MuxManager
    *
    *@brief class destructor
    */
    virtual ~MuxManager() = default;

    /**
    *@method getIoService
    *
    *@brief getter for Boost IO Service/Context object
    *
    *@return reference to Boost IO Service/Context object
    */
    inline boost::asio::io_service& getIoService() {return mIoService;};

    /**
    *@method getDbInterface
    *
    *@brief getter for DbInterface object
    *
    *@return reference to DbInterface object
    */
    inline mux::DbInterface& getDbInterface() {return mDbInterface;};

    /**
    *@method setTimeoutIpv4_msec
    *
    *@brief setter for IPv4 LinkProber timeout in msec
    *
    *@param timeout_msec (in)  timeout in msec
    *
    *@return none
    */
    inline void setTimeoutIpv4_msec(uint32_t timeout_msec) {mMuxConfig.setTimeoutIpv4_msec(timeout_msec);};

    /**
    *@method setTimeoutIpv6_msec
    *
    *@brief setter for IPv6 LinkProber timeout in msec
    *
    *@param timeout_msec (in)  timeout in msec
    *
    *@return none
    */
    inline void setTimeoutIpv6_msec(uint32_t timeout_msec) {mMuxConfig.setTimeoutIpv6_msec(timeout_msec);};

    /**
    *@method setPositiveStateChangeRetryCount
    *
    *@brief setter for LinkProber positive state change retry count
    *
    *@param stateChangeRetryCount (in)  state change retry count
    *
    *@return none
    */
    inline void setPositiveStateChangeRetryCount(uint32_t stateChangeRetryCount) {
        mMuxConfig.setPositiveStateChangeRetryCount(stateChangeRetryCount);
    };

    /**
    *@method setNegativeStateChangeRetryCount
    *
    *@brief setter for LinkProber negative state change retry count
    *
    *@param stateChangeRetryCount (in)  state change retry count
    *
    *@return none
    */
    inline void setNegativeStateChangeRetryCount(uint32_t stateChangeRetryCount) {
        mMuxConfig.setNegativeStateChangeRetryCount(stateChangeRetryCount);
    };

    /**
    *@method setSuspendTimeout_msec
    *
    *@brief setter for LinkProber suspend timer timeout
    *
    *@param suspendTimeout_msec (in)  suspend timer timeout
    *
    *@return none
    */
    inline void setSuspendTimeout_msec(uint32_t suspendTimeout_msec) {mMuxConfig.setSuspendTimeout_msec(suspendTimeout_msec);};

    /**
    *@method setSuspendTimeout_msec
    *
    *@brief setter for LinkProber suspend timer timeout
    *
    *@param suspendTimeout_msec (in)  suspend timer timeout
    *
    *@return none
    */
    inline void setLoopbackIpv4Address(boost::asio::ip::address& address) {mMuxConfig.setLoopbackIpv4Address(address);};

    /**
    *@method initialize
    *
    *@brief initialize MuxManager class and creates DbInterface instance that reads/listen from/to Redis db
    *
    *@return none
    */
    void initialize();

    /**
    *@method deinitialize
    *
    *@brief deinitialize MuxManager class and deinitialize DbInterface instance
    *
    *@return none
    */
    void deinitialize();

    /**
    *@method run
    *
    *@brief start Boost IO Service event loop
    *
    *@return none
    */
    void run();

    /**
    *@method terminate
    *
    *@brief stop and terminate Boost IO Service event loop
    *
    *@return none
    */
    void terminate();

    /**
    *@method addOrUpdateMuxPort
    *
    *@brief update MUX port server/blade IPv4 Address. If port is not found, create new MuxPort object
    *
    *@param portName (in)           Mux port name
    *@param smartNicIpAddress (in)  server/blade IP address
    *
    *@return none
    */
    void addOrUpdateMuxPort(const std::string &portName, boost::asio::ip::address smartNicIpAddress);

    /**
    *@method updateMuxPortConfig
    *
    *@brief update MUX port server/blade IPv4 Address. If port is not found, create new MuxPort object
    *
    *@param portName (in)   Mux port name
    *@param linkState (in)  Mux port link state
    *
    *@return none
    */
    void updateMuxPortConfig(const std::string &portName, const std::string &linkState);

    /**
    *@method addOrUpdateMuxPortLinkState
    *
    *@brief update MUX port server/blade IPv4 Address. If port is not found, create new MuxPort object
    *
    *@param portName (in)   Mux port name
    *@param linkState (in)  Mux port link state
    *
    *@return none
    */
    void addOrUpdateMuxPortLinkState(const std::string &portName, const std::string &linkState);

    /**
    *@method addOrUpdateMuxPortMuxState
    *
    *@brief update MUX port state db notification
    *
    *@param portName (in)   Mux port name
    *@param muxState (in)   Mux port state
    *
    *@return none
    */
    void addOrUpdateMuxPortMuxState(const std::string &portName, const std::string &muxState);

    /**
    *@method processGetServerMacAddress
    *
    *@brief update MUX port server MAC address
    *
    *@param portName (in)   Mux port name
    *@param address (in)    Server MAC address
    *
    *@return none
    */
    void processGetServerMacAddress(const std::string &portName, const std::array<uint8_t, ETHER_ADDR_LEN> &address);

    /**
    *@method processGetMuxState
    *
    *@brief update MUX port app db notification
    *
    *@param portName (in)   Mux port name
    *@param muxState (in)   Mux port state
    *
    *@return none
    */
    void processGetMuxState(const std::string &portName, const std::string &muxState);

    /**
    *@method processProbeMuxState
    *
    *@brief update MUX port app db notification
    *
    *@param portName (in)   Mux port name
    *@param muxState (in)   Mux port state
    *
    *@return none
    */
    void processProbeMuxState(const std::string &portName, const std::string &muxState);

private:
    /**
    *@method getMuxPortPtrOrThrow
    *
    *@brief retrieve a pointer to MuxPort if it exist or create a new MuxPort object
    *
    *@param portName (in)   Mux port name
    *
    *@return pointer to MuxPort object
    */
    std::shared_ptr<MuxPort> getMuxPortPtrOrThrow(const std::string &portName);

    /**
    *@method handleSignal
    *
    *@brief handles system signal
    *
    *@param errorCode (in)      Boost error code
    *@param signalNumber (in)   Signal number
    *
    *@return none
    */
    void handleSignal(const boost::system::error_code errorCode, int signalNumber);

    /**
    *@method handleProcessTerminate
    *
    *@brief stop DB interface thread and stop boost io service
    *
    *@return none
    */
    void handleProcessTerminate();

private:
    common::MuxConfig mMuxConfig;

    boost::asio::io_service mIoService;
    boost::asio::io_service::work mWork;
    boost::thread_group mThreadGroup;
    boost::asio::signal_set mSignalSet;

    mux::DbInterface mDbInterface;

    PortMap mPortMap;
};

} /* namespace mux */

#endif /* MUXMANAGER_H_ */

/*
 * MuxManagerTest.h
 *
 *  Created on: Jun 4, 2021
 *      Author: taahme
 */

#ifndef MUXMANAGERTEST_H_
#define MUXMANAGERTEST_H_

#include <memory>
#include <tuple>
#include "gtest/gtest.h"

#include "FakeDbInterface.h"
#include "FakeLinkProber.h"
#include "NetMsgInterface.h"

namespace mux {
class MuxManager;
}

namespace test
{

class MuxManagerTest: public testing::Test
{
public:
    MuxManagerTest();
    virtual ~MuxManagerTest() = default;

    void runIoService(uint32_t count = 1);
    common::MuxPortConfig::Mode getMode(std::string port);
    uint32_t getPositiveStateChangeRetryCount(std::string port);
    uint32_t getNegativeStateChangeRetryCount(std::string port);
    uint32_t getTimeoutIpv4_msec(std::string port);
    uint32_t getTimeoutIpv6_msec(std::string port);
    uint32_t getLinkWaitTimeout_msec(std::string port);
    boost::asio::ip::address getBladeIpv4Address(std::string port);
    std::array<uint8_t, ETHER_ADDR_LEN> getBladeMacAddress(std::string port);
    boost::asio::ip::address getLoopbackIpv4Address(std::string port);
    std::array<uint8_t, ETHER_ADDR_LEN> getTorMacAddress(std::string port);
    void processMuxPortConfigNotifiction(std::deque<swss::KeyOpFieldsValuesTuple> &entries);
    link_manager::LinkManagerStateMachine::CompositeState getCompositeStateMachineState(std::string port);
    void processServerIpAddress(std::vector<swss::KeyOpFieldsValuesTuple> &servers);
    void processServerMacAddress(std::string port, std::array<char, MAX_ADDR_SIZE + 1> ip, std::array<char, MAX_ADDR_SIZE + 1> mac);
    void processLoopback2InterfaceInfo(std::vector<std::string> &loopbackIntfs);
    void processTorMacAddress(std::string &mac);
    void processMuxResponseNotifiction(std::deque<swss::KeyOpFieldsValuesTuple> &entries);
    void processMuxLinkmgrConfigNotifiction(std::deque<swss::KeyOpFieldsValuesTuple> &entries);
    void updateServerMacAddress(boost::asio::ip::address serverIp, const uint8_t *serverMac);
    void processGetMuxState(const std::string &portName, const std::string &muxState);
    void createPort(std::string port);

public:
    std::shared_ptr<mux::MuxManager> mMuxManagerPtr;
    std::shared_ptr<FakeDbInterface> mDbInterfacePtr;
    mux::NetMsgInterface mNetMsgInterface;

    std::shared_ptr<FakeLinkProber> mFakeLinkProber;
};

class MuxResponseTest: public MuxManagerTest,
                       public testing::WithParamInterface<std::tuple<std::string, uint32_t, mux_state::MuxState::Label>>
{
};

class GetMuxStateTest: public MuxManagerTest,
                       public testing::WithParamInterface<std::tuple<std::string, mux_state::MuxState::Label>>
{
};

class MuxConfigUpdateTest: public MuxManagerTest,
                           public testing::WithParamInterface<std::tuple<std::string, common::MuxPortConfig::Mode>>
{
};

} /* namespace test */

#endif /* MUXMANAGERTEST_H_ */

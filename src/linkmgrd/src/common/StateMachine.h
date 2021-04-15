/*
 * StateMachine.h
 *
 *  Created on: Oct 4, 2020
 *      Author: tamer
 */

#ifndef STATEMACHINE_H_
#define STATEMACHINE_H_

#include <memory>

#include <boost/asio.hpp>

#include "common/MuxPortConfig.h"

namespace link_manager {
class LinkManagerStateMachine;
}

namespace link_prober {
class LinkProberStateMachine;
}

namespace mux_state {
class MuxStateMachine;
}

namespace link_state {
class LinkStateMachine;
}

namespace common
{
class State;

/**
 *@class StateMachine
 *
 *@brief Maintains common state machine functionality; current state,
 *       serialization object (strand,) and MuxPortConfig object
 */
class StateMachine
{
public:
    /**
    *@method StateMachine
    *
    *@brief class default constructor
    */
    StateMachine() = delete;

    /**
    *@method StateMachine
    *
    *@brief class copy constructor
    *
    *@param StateMachine (in)  reference to StateMachine object to be copied
    */
    StateMachine(const StateMachine &) = delete;

    /**
    *@method StateMachine
    *
    *@brief class constructor
    *
    *@param strand (in)         boost serialization object
    *@param muxPortConfig (in)  reference to MuxPortConfig object
    */
    StateMachine(
        boost::asio::io_service::strand &strand,
        MuxPortConfig &muxPortConfig
    );

    /**
    *@method ~StateMachine
    *
    *@brief class destructor
    */
    virtual ~StateMachine() = default;

    /**
    *@method getStrand
    *
    *@brief getter for boost serialization object
    *
    *@return reference to boost serialization object
    */
    boost::asio::io_service::strand& getStrand() {return mStrand;};

private:
    friend class link_manager::LinkManagerStateMachine;
    friend class link_prober::LinkProberStateMachine;
    friend class mux_state::MuxStateMachine;
    friend class link_state::LinkStateMachine;

    /**
    *@method setCurrentState
    *
    *@brief setter for current state
    *
    *@param state (in)  current state of the state machine
    *
    *@return none
    */
    void setCurrentState(State* state);

    /**
    *@method getCurrentState
    *
    *@brief getter for current state
    *
    *@return current state of the state machine
    */
    State* getCurrentState() {return mCurrentState;};

    /**
    *@method getMuxPortConfig
    *
    *@brief getter MuxPortConfig object
    *
    *@return reference to MuxPortConfig object
    */
    const MuxPortConfig& getMuxPortConfig() const {return mMuxPortConfig;};

private:
    boost::asio::io_service::strand mStrand;
    State *mCurrentState = nullptr;
    MuxPortConfig &mMuxPortConfig;
};

} /* namespace common */

#endif /* STATEMACHINE_H_ */

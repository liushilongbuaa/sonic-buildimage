/*
 * MuxState.h
 *
 *  Created on: Oct 18, 2020
 *      Author: tamer
 */

#ifndef MUX_STATE_MUXSTATE_H_
#define MUX_STATE_MUXSTATE_H_

#include <common/State.h>

namespace mux_state
{
class MuxStateMachine;
class ActiveEvent;
class StandbyEvent;
class UnknownEvent;

/**
 *@class MuxState
 *
 *@brief base class for different Mux states
 */
class MuxState: public common::State
{
public:
    /**
     *@enum Label
     *
     *@brief Label corresponding to each MuxState State
     */
    enum Label {
        Active,
        Standby,
        Unknown,
        Wait,

        Count
    };

public:
    /**
    *@method MuxState
    *
    *@brief class default constructor
    */
    MuxState() = delete;

    /**
    *@method MuxState
    *
    *@brief class copy constructor
    *
    *@param MuxState (in)  reference to MuxState object to be copied
    */
    MuxState(const MuxState &) = delete;

    /**
    *@method MuxState
    *
    *@brief class constructor
    *
    *@param stateMachine (in)   reference to MuxStateMachine object
    *@param muxPortConfig (in)  reference to MuxPortConfig object
    */
    MuxState(
        MuxStateMachine &stateMachine,
        common::MuxPortConfig &muxPortConfig
    );

    /**
    *@method ~MuxState
    *
    *@brief class destructor
    */
    virtual ~MuxState() = default;

    /**
    *@method handleEvent
    *
    *@brief handle ActiveEvent from state db/xcvrd
    *
    *@param event (in)  reference to ActiveEvent
    *
    *@return pointer to next MuxState
    */
    virtual MuxState* handleEvent(ActiveEvent &event) = 0;

    /**
    *@method handleEvent
    *
    *@brief handle StandbyEvent from state db/xcvrd
    *
    *@param event (in)  reference to StandbyEvent
    *
    *@return pointer to next MuxState
    */
    virtual MuxState* handleEvent(StandbyEvent &event) = 0;

    /**
    *@method handleEvent
    *
    *@brief handle UnknownEvent from state db/xcvrd
    *
    *@param event (in)  reference to UnknownEvent
    *
    *@return pointer to next MuxState
    */
    virtual MuxState* handleEvent(UnknownEvent &event) = 0;

    /**
    *@method resetState
    *
    *@brief reset current state attributes
    *
    *@return none
    */
    virtual MuxState::Label getStateLabel() = 0;
};

} /* namespace mux_state */

#endif /* MUX_STATE_MUXSTATE_H_ */

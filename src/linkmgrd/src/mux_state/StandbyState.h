/*
 * StandbyState.h
 *
 *  Created on: Oct 20, 2020
 *      Author: tamer
 */

#ifndef MUX_STATE_STANDBYSTATE_H_
#define MUX_STATE_STANDBYSTATE_H_

#include <mux_state/MuxState.h>

namespace mux_state
{

/**
 *@class StandbyState
 *
 *@brief maintains StandbyState state of MuxState
 */
class StandbyState: public MuxState
{
public:
    /**
    *@method StandbyState
    *
    *@brief class default constructor
    */
    StandbyState() = delete;

    /**
    *@method StandbyState
    *
    *@brief class copy constructor
    *
    *@param StandbyState (in)  reference to StandbyState object to be copied
    */
    StandbyState(const StandbyState &) = delete;

    /**
    *@method StandbyState
    *
    *@brief class constructor
    *
    *@param stateMachine (in)   reference to LinkStateMachine
    *@param muxPortConfig (in)  reference to MuxPortConfig object
    */
    StandbyState(
        MuxStateMachine &stateMachine,
        common::MuxPortConfig &muxPortConfig
    );

    /**
    *@method ~StandbyState
    *
    *@brief class destructor
    */
    virtual ~StandbyState() = default;

    /**
    *@method handleEvent
    *
    *@brief handle ActiveEvent from state db/xcvrd
    *
    *@param event (in)  reference to ActiveEvent
    *
    *@return pointer to next MuxState
    */
    virtual MuxState* handleEvent(ActiveEvent &event) override;

    /**
    *@method handleEvent
    *
    *@brief handle StandbyEvent from state db/xcvrd
    *
    *@param event (in)  reference to StandbyEvent
    *
    *@return pointer to next MuxState
    */
    virtual MuxState* handleEvent(StandbyEvent &event) override;

    /**
    *@method handleEvent
    *
    *@brief handle UnknownEvent from state db/xcvrd
    *
    *@param event (in)  reference to UnknownEvent
    *
    *@return pointer to next MuxState
    */
    virtual MuxState* handleEvent(UnknownEvent &event) override;

    /**
    *@method handleEvent
    *
    *@brief handle ErrorEvent from state db
    *
    *@param event (in)  reference to ErrorEvent
    *
    *@return pointer to next MuxState
    */
    virtual MuxState* handleEvent(ErrorEvent &event) override;

    /**
    *@method resetState
    *
    *@brief reset current state attributes
    *
    *@return none
    */
    virtual void resetState() override;

    /**
    *@method getStateLabel
    *
    *@brief getter for MuxState label
    *
    *@return MuxState Standby label
    */
    virtual MuxState::Label getStateLabel() override {return MuxState::Label::Standby;};

private:
    uint8_t mActiveEventCount = 0;
    uint8_t mUnknownEventCount = 0;
    uint8_t mErrorEventCount = 0;
};

} /* namespace mux_state */

#endif /* MUX_STATE_STANDBYSTATE_H_ */

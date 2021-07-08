/*
 * StandbyState.h
 *
 *  Created on: Oct 7, 2020
 *      Author: tamer
 */

#ifndef LINK_PROBER_STANDBYSTATE_H_
#define LINK_PROBER_STANDBYSTATE_H_

#include "LinkProberState.h"

namespace link_prober
{
class LinkProberStateMachine;

/**
 *@class StandbyState
 *
 *@brief maintains Standby state of LinkProber
 */
class StandbyState : public LinkProberState
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
    *@param stateMachine (in)   reference to LinkProberStateMachine
    *@param muxPortConfig (in)  reference to MuxPortConfig object
    */
    StandbyState(
        LinkProberStateMachine &stateMachine,
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
    *@brief handle IcmpPeerEvent from LinkProber
    *
    *@param event (in)  reference to IcmpPeerEvent
    *
    *@return pointer to next LinkProberState
    */
    virtual LinkProberState* handleEvent(IcmpPeerEvent &event) override;

    /**
    *@method handleEvent
    *
    *@brief handle IcmpSelfEvent from LinkProber
    *
    *@param event (in)  reference to IcmpSelfEvent
    *
    *@return pointer to next LinkProberState
    */
    virtual LinkProberState* handleEvent(IcmpSelfEvent &event) override;

    /**
    *@method handleEvent
    *
    *@brief handle IcmpUnknownEvent from LinkProber
    *
    *@param event (in)  reference to IcmpUnknownEvent
    *
    *@return pointer to next LinkProberState
    */
    virtual LinkProberState* handleEvent(IcmpUnknownEvent &event) override;

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
    *@brief getter for LinkeProberState label
    *
    *@return LinkProberState Standby label
    */
    virtual LinkProberState::Label getStateLabel() override {return LinkProberState::Label::Standby;};

private:
    uint8_t mSelfEventCount = 0;
    uint8_t mUnknownEventCount = 0;
};

} /* namespace link_prober */

#endif /* LINK_PROBER_STANDBYSTATE_H_ */

/*
 * UpState.h
 *
 *  Created on: Oct 20, 2020
 *      Author: tamer
 */

#ifndef LINK_STATE_UPSTATE_H_
#define LINK_STATE_UPSTATE_H_

#include <link_state/LinkState.h>

namespace link_state
{

/**
 *@class DownState
 *
 *@brief maintains DownState state of LinkState
 */
class UpState: public LinkState
{
public:
    /**
    *@method UpState
    *
    *@brief class default constructor
    */
    UpState() = delete;

    /**
    *@method UpState
    *
    *@brief class copy constructor
    *
    *@param UpState (in)  reference to UpState object to be copied
    */
    UpState(const UpState &) = delete;

    /**
    *@method UpState
    *
    *@brief class constructor
    *
    *@param stateMachine (in)   reference to LinkStateMachine
    *@param muxPortConfig (in)  reference to MuxPortConfig object
    */
    UpState(
        LinkStateMachine &stateMachine,
        common::MuxPortConfig &muxPortConfig
    );

    /**
    *@method ~UpState
    *
    *@brief class destructor
    */
    virtual ~UpState() = default;

    /**
    *@method handleEvent
    *
    *@brief handle UpEvent from state db
    *
    *@param event (in)  reference to UpEvent
    *
    *@return pointer to next LinkState
    */
    virtual LinkState* handleEvent(UpEvent &event) override;

    /**
    *@method handleEvent
    *
    *@brief handle DownEvent from state db
    *
    *@param event (in)  reference to DownEvent
    *
    *@return pointer to next LinkState
    */
    virtual LinkState* handleEvent(DownEvent &event) override;

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
    *@brief getter for LinkState label
    *
    *@return LinkState Up label
    */
    virtual LinkState::Label getStateLabel() override {return LinkState::Label::Up;};

private:
    uint8_t mDownEventCount = 0;
};

} /* namespace link_state */

#endif /* LINK_STATE_UPSTATE_H_ */

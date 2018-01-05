#include <functional>

class Button
{
  unsigned      pin_;
  unsigned long debounce_;
  unsigned long press_start_;
  bool          was_pressed_;

public:
  Button( unsigned pin, unsigned debounce )
    : pin_( pin )
    , debounce_( debounce )
    , press_start_( millis() )
    , was_pressed_( false )
  {
  }

  void begin()
  {
    pinMode( pin_, INPUT_PULLUP );
  }

  void check( std::function< void() > callback )
  {
    if ( digitalRead( pin_ ) == HIGH )
    {
      if ( was_pressed_ )  // button was pressed previously
      {
        return;
      }
      else  // button was not pressed previously
      {
        press_start_ = millis();
        was_pressed_ = true;
      }
    }
    else  // pin_ is LOW
    {
      if ( was_pressed_ )  // button was pressed previously
      {
        if ( millis() - press_start_ > debounce_ )
        {
          if ( callback )
          {
            callback();
          }
        }
        was_pressed_ = false;
      }
      else  // button was not pressed previously
      {
        return;
      }
    }
  }
};

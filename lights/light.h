
class Light
{
  unsigned pin_;
  bool     enabled_;

public:
  Light( unsigned pin )
    : pin_( pin )
    , enabled_( false )
  {
  }

  void begin()
  {
    pinMode( pin_, OUTPUT );
    digitalWrite( pin_, LOW );
  };

  void enable()
  {
    digitalWrite( pin_, HIGH );
    enabled_ = true ;
  }
  void disable()
  {
    digitalWrite( pin_, LOW );
    enabled_ = false ;
  }
  bool isEnabled()
  {
    return enabled_;
  }
};

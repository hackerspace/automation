#pragma once

namespace util
{

#define STEP()                  \
  Serial.print( millis() );     \
  Serial.print( ": " );         \
  Serial.print( __FUNCTION__ ); \
  Serial.print( "() in " );     \
  Serial.print( __FILE__ );     \
  Serial.print( ':' );          \
  Serial.println( __LINE__ );
}

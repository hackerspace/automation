
#include "button.h"
#include "light.h"
#include "wifi.h"
#include <ESP8266WiFi.h>

Button button( 14, 100 );
Light  light1( 5 );
Light  light2( 4 );

WiFiStack wifi_stack( WiFiConfig( "Base48.cz-IoT", "penis", 1337 ) );

void enableLights()
{
  Serial.println( "Enabling lights" );
  light1.enable();
  light2.enable();
}

void disableLights()
{
  Serial.println( "Disabling lights" );
  light1.disable();
  light2.disable();
}

void buttonEvent()
{
  if ( light1.isEnabled() || light2.isEnabled() )
  {
    disableLights();
  }
  else
  {
    enableLights();
  }
}

void setup( void )
{
  Serial.begin( 115200 );

  button.begin();
  light1.begin();
  light2.begin();

  wifi_stack.begin();
}

void processAvailableClient( WiFiClient& client )
{

  String data = client.readString();

  for ( unsigned i = 0; i < data.length(); ++i )
  {
    switch ( data[i] )
    {
      case 'e':
      case 'E':
        enableLights();
        client.println( "Lights are enabled" );
        break;
      case 'd':
      case 'D':
        disableLights();
        client.println( "Lights are disabled" );
        break;
      default:
        break;
    }
  }
}

void processNewClient( WiFiClient& client )
{
  client.println( "Welcome to esp IoT conrol, write 'e' for enabling and 'd' for disabling" );
}

void loop( void )
{
  button.check( buttonEvent );
  wifi_stack.tick();
  wifi_stack.checkClientData( processAvailableClient );
  wifi_stack.checkNewClient( processNewClient );
  wifi_stack.printInfoThrottled< 1000 >( Serial );
}

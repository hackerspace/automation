#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <WiFiServer.h>
#include <functional>
#include <array>
#include <algorithm>

#define CLIENTS_N 2

struct WiFiConfig
{
  String   ssid;
  String   password;
  unsigned server_port;

  WiFiConfig( String ssidarg, String passarg, unsigned portarg )
    : ssid( ssidarg )
    , password( passarg )
    , server_port( portarg )
  {
  }
};

class WiFiStack
{

public:
  WiFiStack( const WiFiConfig config )
    : config_( config )
    , server_( config.server_port )
    , clients_()
    , last_print_( 0 )
  {
  }

  void begin()
  {
    WiFi.begin( config_.ssid.c_str(), config_.password.c_str() );
  }

  bool isConnected()
  {
    return WiFi.status() == WL_CONNECTED;
  }

  void tick()
  {
    if ( server_.status() == CLOSED )
    {
      if ( isConnected() )
      {
        server_.begin();
      }
    }
  }

  void checkClientData( std::function< void( WiFiClient& ) > available_client_callback )
  {
    std::for_each( clients_.begin(), clients_.end(), [&]( WiFiClient& client ) {
      if ( !client )
      {
        return;
      }

      if ( !client.available() )
      {
        return;
      }
      if ( available_client_callback )
      {
        available_client_callback( client );
      }
    } );
  }

  void checkNewClient( std::function< void( WiFiClient& ) > new_client_callback )
  {
    WiFiClient new_client = server_.available();
    if ( !new_client )
    {
      return;
    }

    auto iter = std::find_if( clients_.begin(), clients_.end(), []( WiFiClient& client ) {
      return !bool( client );  // checks if client is active
    } );

    if ( iter == clients_.end() )
    {
      replaceClient( *clients_.begin(), new_client );
      iter = clients_.begin();
    }
    else
    {
      *iter = new_client;
    }

    new_client_callback( *iter );
  }

  void printInfo( Stream& output )
  {
    if ( isConnected() )
    {
      output.print( "Connected to " );
      output.println( config_.ssid );
      output.print( "IP address: " );
      output.println( WiFi.localIP() );
    }
    else
    {
      output.println( "Not connected" );
    }
  }

  /*
   * @period - period in milliseconds, print won't be printed more frequently than 'period' milliseconds
   */
  template < unsigned period >
  void printInfoThrottled( Stream& output )
  {
    if ( last_print_ + period < millis() )
    {
      printInfo( output );
      last_print_ = millis();
    }
  }

private:
  const WiFiConfig             config_;
  WiFiServer                   server_;
  std::array< WiFiClient, 5 > clients_;
  unsigned long                last_print_;

  void replaceClient( WiFiClient& old, WiFiClient& newc )
  {
    old.println( "Kicked" );
    old.stop();
    newc.println( "You have kicked a client" );

    old = newc;
  }
};

#include <WiFi.h>
#include <Wire.h>

#include "esp_wifi.h"


/* Refer to https://www.hackster.io/p99will/esp32-wifi-mac-scanner-sniffer-promiscuous-4c12f4 */


String maclist[256];
int macListSize = 256;
int listcount = 0;

const wifi_promiscuous_filter_t filt={ //Idk what this does
    .filter_mask=WIFI_PROMIS_FILTER_MASK_MGMT|WIFI_PROMIS_FILTER_MASK_DATA
};

typedef struct { // or this
  uint8_t mac[6];
} __attribute__((packed)) MacAddr;

typedef struct { // still dont know much about this
  int16_t fctl;
  int16_t duration;
  MacAddr da;
  MacAddr sa;
  MacAddr bssid;
  int16_t seqctl;
  unsigned char payload[];
} __attribute__((packed)) WifiMgmtHdr;


#define maxCh 13 //max Channel -> US = 11, EU = 13, Japan = 14


int curChannel = 1;

void sniffer(void* buf, wifi_promiscuous_pkt_type_t type) { //This is where packets end up after they get sniffed
  wifi_promiscuous_pkt_t *p = (wifi_promiscuous_pkt_t*)buf; // Dont know what these 3 lines do
  int len = p->rx_ctrl.sig_len;
  WifiMgmtHdr *wh = (WifiMgmtHdr*)p->payload;
  len -= sizeof(WifiMgmtHdr);
  if (len < 0){
    Serial.println("Receuved 0");
    return;
  }
  String packet;
  String mac;
  int fctl = ntohs(wh->fctl);
  for(int i=8;i<=p->rx_ctrl.sig_len;i++){ // This reads the first couple of bytes of the packet. This is where you can read the whole packet replaceing the "8+6+1" with "p->rx_ctrl.sig_len"
     packet += String(p->payload[i],HEX);
  }

  for(int i=4;i<=15;i++){ // This removes the 'nibble' bits from the stat and end of the data we want. So we only get the mac address.
    mac += packet[i];
  }
  mac.toUpperCase();

  bool added = false;
  for(int i=0; i<=listcount; i++){ // checks if the MAC address has been added before
    if(mac == maclist[i]){
      added = true;
    }
  }

  if (!added) { // If its new. add it to the array.
    maclist[listcount] = mac;

    listcount ++;
    if(listcount >= macListSize){
      Serial.println("Too many addresses");
      listcount = 0;
    }
  }
}



//===== SETUP =====//
void setup() {

  /* start Serial */
  Serial.begin(9600);

  /* setup wifi */
  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  esp_wifi_init(&cfg);
  esp_wifi_set_storage(WIFI_STORAGE_RAM);
  esp_wifi_set_mode(WIFI_MODE_NULL);
  esp_wifi_start();
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_promiscuous_filter(&filt);
  esp_wifi_set_promiscuous_rx_cb(&sniffer);
  esp_wifi_set_channel(curChannel, WIFI_SECOND_CHAN_NONE);

  Serial.println("starting!");
}

void showMacAddresses(bool online){

//{
//  "mac_count ": 135
//}
Serial.println("{ \"Id\" : \"mac\", \"mac_count\" : " + String(listcount) + "}");
  //for(int i=0; i<listcount; i++) {
    //Serial.println("Mac:" + maclist[i]);
  //}
}

//===== LOOP =====//
void loop() {
    //Serial.println("Changed channel:" + String(curChannel));
    if(curChannel > maxCh){
      curChannel = 1;
    }
    esp_wifi_set_channel(curChannel, WIFI_SECOND_CHAN_NONE);
    delay(1000);
    showMacAddresses(false);
    curChannel++;
}

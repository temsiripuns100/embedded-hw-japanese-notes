#include <stdio.h>
#include <unistd.h>      // 遅延処理用のusleep関数
#include "system.h"      // ベースアドレス定義ヘッダ
#include "io.h"          // レジスタ直叩き用I/Oマクロ

// カスタムIPのベースアドレス設定
// (Platform Designerで自動生成されたsystem.hの定数を流用)
#define LED_BASE SIMPLE_LED_AVALON_0_BASE

// VHDL設計に基づいたバイトオフセット値
#define OFFSET_LED0 0x0
#define OFFSET_LED1 0x4
#define OFFSET_LED2 0x8
#define OFFSET_LED3 0xC

int main()
{
    printf("Nios II Custom LED Control Started!\n");
    
    // 起動時にすべてのLEDを消灯
    IOWR_32DIRECT(LED_BASE, OFFSET_LED0, 0);
    IOWR_32DIRECT(LED_BASE, OFFSET_LED1, 0);
    IOWR_32DIRECT(LED_BASE, OFFSET_LED2, 0);
    IOWR_32DIRECT(LED_BASE, OFFSET_LED3, 0);
    
    while(1)
    {
        // 1. LEDを順番に点灯（LED0 -> LED1 -> LED2 -> LED3）
        printf("LED chasing sequence started...\n");
        
        IOWR_32DIRECT(LED_BASE, OFFSET_LED0, 1); // LED0点灯
        usleep(500000); // 500ms遅延（デバッグ用に見やすく設定）
        IOWR_32DIRECT(LED_BASE, OFFSET_LED0, 0); // LED0消灯
        
        IOWR_32DIRECT(LED_BASE, OFFSET_LED1, 1); // LED1点灯
        usleep(500000); // 500ms遅延
        IOWR_32DIRECT(LED_BASE, OFFSET_LED1, 0); // LED1消灯
        
        IOWR_32DIRECT(LED_BASE, OFFSET_LED2, 1); // LED2点灯
        usleep(500000); // 500ms遅延
        IOWR_32DIRECT(LED_BASE, OFFSET_LED2, 0); // LED2消灯
        
        IOWR_32DIRECT(LED_BASE, OFFSET_LED3, 1); // LED3点灯
        usleep(500000); // 500ms遅延
        IOWR_32DIRECT(LED_BASE, OFFSET_LED3, 0); // LED3消灯
        
        usleep(1000000); // 次のシーケンス開始まで1秒待機
    }
    
    return 0;
}

#include "GHOST_SparkleUpdater.h"
#include "Sparkle/SPUUpdaterDelegate.h"
#include "Sparkle/SPUUpdater.h"
#include "Sparkle/SPUStandardUpdaterController.h"

SPUUpdater *spuUpdater = nil;

@interface SparkleDelegate : NSObject <SPUUpdaterDelegate> {
}
@end

@implementation SparkleDelegate {
  SparkleUpdater *u;
}

- (void)setUpdater:(SparkleUpdater *)v {
  u = v;
}
@end

SparkleUpdater::SparkleUpdater() {
  SparkleDelegate *delegate = [[SparkleDelegate alloc] init];
  [delegate setUpdater:this];

  SPUStandardUpdaterController *updaterController = [SPUStandardUpdaterController alloc];
  [updaterController initWithStartingUpdater:YES updaterDelegate:delegate userDriverDelegate:Nil];

  spuUpdater = updaterController.updater;
}

SparkleUpdater::~SparkleUpdater() {
  [spuUpdater release];
  spuUpdater = nil;
}

void SparkleUpdater::checkForUpdates() {
  [spuUpdater checkForUpdates];
}
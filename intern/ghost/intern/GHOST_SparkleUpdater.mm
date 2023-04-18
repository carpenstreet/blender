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

bool SparkleUpdater::getAutomaticDownload() const {
  return spuUpdater.automaticallyDownloadsUpdates;
}

void SparkleUpdater::setAutomaticDownload(bool value) {
  spuUpdater.automaticallyDownloadsUpdates = value;
}

void SparkleUpdater::checkAndShowUI() {
  [spuUpdater checkForUpdates];
}

void SparkleUpdater::checkAndMaybeShowUI() {
  [spuUpdater checkForUpdatesInBackground];
}

void SparkleUpdater::checkWithoutUI() {
  [spuUpdater checkForUpdateInformation];
}

void SparkleUpdater::checkForUpdates() {
  [spuUpdater checkForUpdates];
}
#pragma once

#ifndef __APPLE__
#  error Apple OSX only!
#endif  // __APPLE__

class SparkleUpdater {
 public:
  SparkleUpdater();
  ~SparkleUpdater();

  bool getAutomaticDownload() const;
  void setAutomaticDownload(bool value);

  void checkAndShowUI();
  void checkAndMaybeShowUI();
  void checkWithoutUI();

  void checkForUpdates();
};
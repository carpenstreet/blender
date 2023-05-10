#pragma once

#ifndef __APPLE__
#  error Apple OSX only!
#endif  // __APPLE__

class SparkleUpdater {
 public:
  SparkleUpdater();
  ~SparkleUpdater();

  void checkForUpdates();
};
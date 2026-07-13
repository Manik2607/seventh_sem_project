package com.facebook.react;

import android.app.Application;
import android.content.Context;
import android.content.res.Resources;

import com.facebook.react.ReactPackage;
import com.facebook.react.shell.MainPackageConfig;
import com.facebook.react.shell.MainReactPackage;
import java.util.Arrays;
import java.util.ArrayList;

@SuppressWarnings("deprecation")
public class PackageList {
  private Application application;
  private ReactNativeHost reactNativeHost;
  private MainPackageConfig mConfig;

  public PackageList(ReactNativeHost reactNativeHost) {
    this(reactNativeHost, null);
  }

  public PackageList(Application application) {
    this(application, null);
  }

  public PackageList(ReactNativeHost reactNativeHost, MainPackageConfig config) {
    this.reactNativeHost = reactNativeHost;
    mConfig = config;
  }

  public PackageList(Application application, MainPackageConfig config) {
    this.reactNativeHost = null;
    this.application = application;
    mConfig = config;
  }

  private ReactNativeHost getReactNativeHost() {
    return this.reactNativeHost;
  }

  private Resources getResources() {
    return this.getApplication().getResources();
  }

  private Application getApplication() {
    if (this.reactNativeHost == null) return this.application;
    return this.reactNativeHost.getApplication();
  }

  private Context getApplicationContext() {
    return this.getApplication().getApplicationContext();
  }

  public ArrayList<ReactPackage> getPackages() {
    return new ArrayList<>(Arrays.<ReactPackage>asList(
      new MainReactPackage(mConfig),
      // @react-native-async-storage/async-storage
      new org.asyncstorage.AsyncStoragePackage(),
      // react-native-geolocation-service
      new com.agontuk.RNFusedLocation.RNFusedLocationPackage(),
      // react-native-gesture-handler
      new com.swmansion.gesturehandler.RNGestureHandlerPackage(),
      // react-native-image-picker
      new com.imagepicker.ImagePickerPackage(),
      // react-native-maps
      new com.rnmaps.maps.MapsPackage(),
      // react-native-permissions
      new com.zoontek.rnpermissions.RNPermissionsPackage(),
      // react-native-reanimated
      new com.swmansion.reanimated.ReanimatedPackage(),
      // react-native-safe-area-context
      new com.th3rdwave.safeareacontext.SafeAreaContextPackage(),
      // react-native-screens
      new com.swmansion.rnscreens.RNScreensPackage(),
      // react-native-worklets
      new com.swmansion.worklets.WorkletsPackage()
    ));
  }
}
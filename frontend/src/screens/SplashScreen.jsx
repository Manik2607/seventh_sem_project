import React, { useEffect } from 'react';
import { View, Text, StyleSheet, StatusBar, useColorScheme } from 'react-native';
import { COLORS } from '../constants/colors';
import { globalStyles, TYPOGRAPHY } from '../styles/globalStyles';

export const SplashScreen = ({ navigation }) => {
  const isDarkMode = useColorScheme() === 'dark';
  const theme = isDarkMode ? COLORS.dark : COLORS.light;

  useEffect(() => {
    // Automatically transition to Login placeholder screen after 2 seconds
    const timer = setTimeout(() => {
      navigation.replace('Login');
    }, 2000);

    return () => clearTimeout(timer);
  }, [navigation]);

  return (
    <View style={[globalStyles.container, globalStyles.center, { backgroundColor: theme.background }]}>
      <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} backgroundColor={theme.background} />
      <View style={styles.contentContainer}>
        <Text style={[styles.title, { color: COLORS.primaryLight }]}>Smart Civic</Text>
        <Text style={[styles.subtitle, { color: theme.textSecondary }]}>Loading Platform...</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  contentContainer: {
    alignItems: 'center',
  },
  title: {
    ...TYPOGRAPHY.h1,
    fontSize: 36,
    fontWeight: '800',
    letterSpacing: 1.5,
    marginBottom: 8,
  },
  subtitle: {
    ...TYPOGRAPHY.body,
    fontSize: 16,
    fontWeight: '500',
  },
});

export default SplashScreen;

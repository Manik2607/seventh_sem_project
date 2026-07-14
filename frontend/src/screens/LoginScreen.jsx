import React from 'react';
import { View, Text, StyleSheet, StatusBar, useColorScheme } from 'react-native';
import { COLORS } from '../constants/colors';
import { globalStyles, TYPOGRAPHY } from '../styles/globalStyles';

export const LoginScreen = () => {
  const isDarkMode = useColorScheme() === 'dark';
  const theme = isDarkMode ? COLORS.dark : COLORS.light;

  return (
    <View style={[globalStyles.container, globalStyles.center, { backgroundColor: theme.background }]}>
      <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} backgroundColor={theme.background} />
      <View style={styles.contentContainer}>
        <Text style={[styles.title, { color: theme.text }]}>Login Screen</Text>
        <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
          Authentication placeholder powered by Redux.
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  contentContainer: {
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  title: {
    ...TYPOGRAPHY.h1,
    fontWeight: '700',
    marginBottom: 12,
  },
  subtitle: {
    ...TYPOGRAPHY.body,
    textAlign: 'center',
  },
});

export default LoginScreen;

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const Home = ({ route }) => {
  const { user } = route.params;

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Welcome, {user.username}!</Text>
      <Text style={styles.text}>Your grade: {user.grade}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#292929',
  },
  text: {
    color: '#FFFFFF',
  },
});

export default Home;

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const Home = ({ route }) => {
  const { user } = route.params;

  return (
    <View style={styles.container}>
      <Text>Welcome, {user.username}!</Text>
      <Text>Your grade: {user.grade}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default Home;

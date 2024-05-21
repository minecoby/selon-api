import { enableScreens } from 'react-native-screens';
enableScreens();

import React from 'react';
import AuthStack from './src/navigation/AuthStack';

const App = () => {
  return <AuthStack />;
};

export default App;

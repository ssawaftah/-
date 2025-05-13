// state.js
let appState = {
  user: null,
  transports: [],
  currentView: 'home'
};

export const updateState = (newState) => {
  appState = {...appState, ...newState};
  render(); // إعادة رسم الواجهة
};

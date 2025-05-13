import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";

const firebaseConfig = {
    apiKey: "AIzaSyBewtf3tVFlRh13WOGkk_dVA1DxvZVDp5I",
    authDomain: "al3arbicv.firebaseapp.com",
    databaseURL: "https://al3arbicv-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "al3arbicv",
    storageBucket: "al3arbicv.appspot.com",
    messagingSenderId: "901851337200",
    appId: "1:901851337200:web:27dace691f0e75481c8d35"
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

export { db };

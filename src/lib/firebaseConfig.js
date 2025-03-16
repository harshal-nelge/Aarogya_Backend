// lib/firebaseConfig.ts
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getDatabase } from "firebase/database";
import { getMessaging } from "firebase/messaging";

export const firebaseConfig = {
    apiKey: "AIzaSyDYXoDiAYJNIHbPOA_VLBdssQ_BfIs3Yys",
    authDomain: "bytecamp-database.firebaseapp.com",
    databaseURL: "https://bytecamp-database-default-rtdb.firebaseio.com",
    projectId: "bytecamp-database",
    storageBucket: "bytecamp-database.firebasestorage.app",
    messagingSenderId: "253609474898",
    appId: "1:253609474898:web:20f39c22b0d95c97b9d88b",
    measurementId: "G-VCZ4HM7BKH"
  };

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getDatabase(app);
const messaging = getMessaging(app);

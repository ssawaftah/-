// مصادقة Firebase
import { initializeApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";

const auth = getAuth();

document.getElementById('loginForm').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            // توجيه المستخدم بعد تسجيل الدخول
            window.location.href = '../index.html';
        })
        .catch((error) => {
            alert('خطأ في تسجيل الدخول: ' + error.message);
        });
});

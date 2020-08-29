importScripts('https://www.gstatic.com/firebasejs/4.8.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/4.8.1/firebase-messaging.js');

// Firebase API key
var config = {
    apiKey: "**************",
    authDomain: "**************.firebaseapp.com",
    databaseURL: "https://**************.firebaseio.com",
    projectId: "**************",
    storageBucket: "**************.appspot.com",
    messagingSenderId: "**************",
    appId: "**************",
    measurementId: "**************"
};
firebase.initializeApp(config);

const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {

    const title = "Messaging Test";
    const options = {
        body: payload.data.status
    };

    return self.registration.showNotification(title, options);
});

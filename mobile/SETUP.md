# CoreKnow Mobile - Setup

## Prerequisites

- Node.js 20+
- Expo Go app on your phone

## First time

    cd mobile
    npm install

## Run on phone

    npx expo start

Scan the QR code with Expo Go.

## Build for Play Store

    npm install -g eas-cli
    eas login
    eas build:configure
    eas build --platform android --profile production
    eas submit --platform android
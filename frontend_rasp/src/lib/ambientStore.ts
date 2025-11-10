// src/lib/ambientStore.ts

type Callback = (humidity: number | null) => void;

let humidity: number | null = null;
const listeners: Callback[] = [];

export function setHumidity(newHum: number | null) {
  humidity = newHum;
  listeners.forEach(listener => listener(humidity));
}

export function subscribeHumidity(callback: Callback) {
  listeners.push(callback);
  // Chame já com o valor atual
  callback(humidity);
  return () => {
    const idx = listeners.indexOf(callback);
    if (idx !== -1) listeners.splice(idx, 1);
  };
}

export function getHumidity() {
  return humidity;
}


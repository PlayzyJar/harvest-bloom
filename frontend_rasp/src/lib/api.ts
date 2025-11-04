// const API_BASE_URL = 'http://192.168.130.166:5000/api';

const API_BASE_URL =
    window.location.origin.replace(/:8080$/, ':5000') + '/api';

export interface LEDStatus {
    status: 'on' | 'off';
}

// LED API functions
export const turnLedOn = async (): Promise<LEDStatus> => {
    const response = await fetch(`${API_BASE_URL}/led/on`, {
        method: 'POST',
    });
    if (!response.ok) {
        throw new Error('Failed to turn LED on');
    }
    return response.json();
};

export const turnLedOff = async (): Promise<LEDStatus> => {
    const response = await fetch(`${API_BASE_URL}/led/off`, {
        method: 'POST',
    });
    if (!response.ok) {
        throw new Error('Failed to turn LED off');
    }
    return response.json();
};

export const getLedStatus = async (): Promise<LEDStatus> => {
    const response = await fetch(`${API_BASE_URL}/led/status`);
    if (!response.ok) {
        throw new Error('Failed to get LED status');
    }
    return response.json();
};

// Ultrasonic (HC-SR04) API
export interface UltrasonicReading {
    distance_cm: number;
}

export const getUltrasonicCurrent = async (): Promise<UltrasonicReading> => {
    const response = await fetch(`${API_BASE_URL}/ultrasonic`);
    if (!response.ok) {
        throw new Error('Failed to get ultrasonic reading');
    }
    return response.json();
};

// NOTE: temperature / humidity / pressure endpoints removed from API surface.
// This front-end only uses the Ultrasonic sensor (HC-SR04). If you need the
// other sensors again, re-add the types and functions here matching your backend.

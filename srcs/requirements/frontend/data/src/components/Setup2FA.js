import { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import api from '../services/api.js';

const Setup2FA = () => {
    const [configData, setConfigData] = useState(null);
    const [token, setToken] = useState('');
    const [step, setStep] = useState('init'); // 'init', '2fa already', 'qr', 'verify'

    const initiate2FASetup = async () => {
        try {
            const response = await api.get('/authentication/auth/2fa/setup/');
            if (response.data && response.data.message === '2FA setup already setup') {
                setStep('2fa already')
                return ;
            }
            setConfigData(response.data);
            setStep('qr');
        } catch (error) {
            console.error('Failed to initiate 2FA:', error);
        }
    };

    const verify2FAToken = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post('/authentication/auth/2fa/setup/', {
                token: token
            });
            if (response.status === 200) {
                setStep('success');
            }
        } catch (error) {
            console.error('Failed to verify 2FA token:', error);
        }
    };

    return (
        <div>
            {step === 'init' && (
                <button onClick={initiate2FASetup}>Setup 2FA</button>
            )}

            {step === '2fa already' && (
                <p>2FA already set</p>
            )}

            {step === 'qr' && configData && (
                <div>
                    <h2>Scan this QR code</h2>
                    <QRCodeSVG value={configData.config_url} size={256} />
                    <p>
                        Or enter this code manually: {configData.secret_key}
                    </p>
                <form onSubmit={verify2FAToken}>
                    <input
                        type="text"
                        value={token}
                        onChange={(e) => setToken(e.target.value)}
                        placeholder="Enter verification code"
                    />
                    <button type="submit">
                        Verify code
                    </button>
                </form>
                </div>
            )}

            {step === 'success' && (
                <div>
                    <h2>2FA Setup complete!</h2>
                    <p>Two-factor authentication has been successfully enabled.</p>
                </div>
            )}
        </div>
    );
};

export default Setup2FA;
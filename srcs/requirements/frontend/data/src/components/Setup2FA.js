import { useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import api from '../services/api';

const Setup2FA = ({ onError }) => {
  const [configData, setConfigData] = useState(null);
  const [token, setToken] = useState('');
  const [step, setStep] = useState('init'); // 'init', '2fa already', 'qr', 'verify'

  const initiate2FASetup = async () => {
    try {
      const response = await api.get('/authentication/auth/2fa/setup/');
      if (response.data?.message === '2FA already set up') {
        setStep('2fa already');
      } else {
        setConfigData(response.data);
        setStep('qr');
      }
    } catch (error) {
      onError('Failed to initiate 2FA setup');
    }
  };

  const verify2FAToken = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/authentication/auth/2fa/setup/', { token });
      if (response.status === 200) setStep('success');
    } catch (error) {
      onError('Failed to verify 2FA token');
    }
  };

  return (
    <div>
      {step === 'init' && <button onClick={initiate2FASetup}>Setup 2FA</button>}
      {step === '2fa already' && <p>2FA is already set up</p>}
      {step === 'qr' && configData && (
        <div>
          <h2>Scan this QR code</h2>
          <QRCodeSVG value={configData.config_url} size={256} />
          <p>Or enter this code manually: {configData.secret_key}</p>
          <form onSubmit={verify2FAToken}>
            <input
              type="text"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Enter verification code"
            />
            <button type="submit">Verify code</button>
          </form>
        </div>
      )}
      {step === 'success' && (
        <div>
          <h2>2FA Setup Complete!</h2>
          <p>Two-factor authentication has been successfully enabled.</p>
        </div>
      )}
    </div>
  );
};

export default Setup2FA;

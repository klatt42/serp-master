import React, { useState, useEffect } from 'react';
import axios from 'axios';

const StatusPanel: React.FC = () => {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await axios.get('http://localhost:8000/health');
        setStatus(response.data);
      } catch (error) {
        setStatus({ status: 'error', message: 'Cannot connect to backend' });
      } finally {
        setLoading(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 10000); // Check every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const statusColor = status?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500';
  const dataforSeoColor = status?.dataforseo_configured ? 'bg-green-500' : 'bg-yellow-500';

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-bold mb-4 text-gray-800">System Status</h2>

      {loading ? (
        <div className="text-gray-600">Checking status...</div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-700 font-medium">Backend API</span>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${statusColor}`}></div>
              <span className="text-sm text-gray-600">
                {status?.status === 'healthy' ? 'Running' : 'Offline'}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-gray-700 font-medium">DataForSEO API</span>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${dataforSeoColor}`}></div>
              <span className="text-sm text-gray-600">
                {status?.dataforseo_configured ? 'Connected' : 'Not Configured'}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-gray-700 font-medium">Service Version</span>
            <span className="text-sm text-gray-600">{status?.version || 'N/A'}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusPanel;

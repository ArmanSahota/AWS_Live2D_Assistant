/**
 * WebSocket Client Module
 * 
 * This module provides a WebSocket client for connecting to the AWS API Gateway WebSocket API.
 * It handles connection management, message sending, and event handling.
 */

import { getIdToken, isLoggedIn } from '../auth/noneAuth';
import { getAWSConfig } from '../../config/appConfig';

// Define the message types
export type Outbound = 
  | { action: 'chat'; text: string; sessionId: string; meta?: Record<string, any> }
  | { action: 'heartbeat'; timestamp: number };

export type Inbound = 
  | { type: 'assistant_text_delta'; text: string }
  | { type: 'assistant_done' }
  | { type: 'server_event'; name: string; data?: any }
  | { type: 'error'; message: string };

export type ConnectionStatus = 'connecting' | 'open' | 'closed' | 'error';

// Define the WebSocket client interface
export interface WSHandle {
  send(msg: Outbound): void;
  onMessage(cb: (m: Inbound) => void): void;
  onStatus(cb: (s: ConnectionStatus) => void): void;
  close(): void;
}

// WebSocket client implementation
class WebSocketClient implements WSHandle {
  private ws: WebSocket | null = null;
  private messageCallbacks: Array<(m: Inbound) => void> = [];
  private statusCallbacks: Array<(s: ConnectionStatus) => void> = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
  private getToken: () => Promise<string | null>;
  private status: ConnectionStatus = 'closed';
  private sessionId: string;

  constructor(getToken: () => Promise<string | null>) {
    this.getToken = getToken;
    this.sessionId = this.generateSessionId();
  }

  /**
   * Generate a unique session ID
   * @returns A unique session ID
   */
  private generateSessionId(): string {
    return `session-${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
  }

  /**
   * Update the connection status and notify listeners
   * @param status The new connection status
   */
  private updateStatus(status: ConnectionStatus): void {
    this.status = status;
    this.statusCallbacks.forEach(cb => cb(status));
  }

  /**
   * Connect to the WebSocket server
   * @returns A promise that resolves when the connection is established
   */
  async connect(): Promise<void> {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const token = await this.getToken();
    if (!token) {
      this.updateStatus('error');
      throw new Error('No authentication token available');
    }

    const config = getAWSConfig();
    const wsUrl = `${config.wsUrl}?token=${encodeURIComponent(token)}`;

    return new Promise<void>((resolve, reject) => {
      try {
        this.updateStatus('connecting');
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          this.reconnectAttempts = 0;
          this.updateStatus('open');
          this.startHeartbeat();
          resolve();
        };

        this.ws.onclose = () => {
          this.updateStatus('closed');
          this.stopHeartbeat();
          this.scheduleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.updateStatus('error');
          reject(error);
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data) as Inbound;
            this.messageCallbacks.forEach(cb => cb(data));
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
      } catch (error) {
        this.updateStatus('error');
        reject(error);
      }
    });
  }

  /**
   * Start sending heartbeat messages
   */
  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      this.send({
        action: 'heartbeat',
        timestamp: Date.now()
      });
    }, 25000); // Send heartbeat every 25 seconds
  }

  /**
   * Stop sending heartbeat messages
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Schedule a reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Maximum reconnection attempts reached');
      return;
    }

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    this.reconnectAttempts++;

    this.reconnectTimeout = setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      this.connect().catch(error => {
        console.error('Reconnection failed:', error);
      });
    }, delay);
  }

  /**
   * Send a message to the WebSocket server
   * @param msg The message to send
   */
  send(msg: Outbound): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not open');
      this.connect().catch(error => {
        console.error('Connection failed:', error);
      });
      return;
    }

    // Add session ID to chat messages if not already present
    if (msg.action === 'chat' && !msg.sessionId) {
      msg.sessionId = this.sessionId;
    }

    try {
      this.ws.send(JSON.stringify(msg));
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }

  /**
   * Register a callback for incoming messages
   * @param cb The callback function
   */
  onMessage(cb: (m: Inbound) => void): void {
    this.messageCallbacks.push(cb);
  }

  /**
   * Register a callback for connection status changes
   * @param cb The callback function
   */
  onStatus(cb: (s: ConnectionStatus) => void): void {
    this.statusCallbacks.push(cb);
    // Immediately call with current status
    cb(this.status);
  }

  /**
   * Close the WebSocket connection
   */
  close(): void {
    this.stopHeartbeat();
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.updateStatus('closed');
  }
}

/**
 * Connect to the WebSocket server
 * @param getToken A function that returns the authentication token
 * @returns A promise that resolves to a WebSocket client
 */
export async function connectWS(getToken: () => Promise<string | null>): Promise<WSHandle> {
  const client = new WebSocketClient(getToken);
  await client.connect();
  return client;
}

// Type definitions for Electron
// This is a simplified declaration file to resolve TypeScript errors

declare module 'electron' {
  // App interface
  interface App {
    getAppPath(): string;
    getPath(name: string): string;
    quit(): void;
    on(event: string, listener: Function): this;
    whenReady(): Promise<void>;
  }

  // WebContents interface
  interface WebContents {
    send(channel: string, ...args: any[]): void;
  }

  // BrowserWindow interface
  interface BrowserWindow {
    webContents: WebContents;
  }

  // IpcMain interface
  interface IpcMainEvent {
    reply(channel: string, ...args: any[]): void;
    sender: WebContents;
  }

  interface IpcMain {
    on(channel: string, listener: (event: IpcMainEvent, ...args: any[]) => void): this;
    once(channel: string, listener: (event: IpcMainEvent, ...args: any[]) => void): this;
    handle(channel: string, handler: (event: IpcMainEvent, ...args: any[]) => Promise<any> | any): void;
    removeHandler(channel: string): void;
    removeAllListeners(channel?: string): this;
  }

  // Basic Electron types
  export const app: App;
  export const BrowserWindow: {
    new(options?: any): BrowserWindow;
    getAllWindows(): BrowserWindow[];
    getFocusedWindow(): BrowserWindow | null;
  };
  export const ipcMain: IpcMain;
  export const ipcRenderer: any;
  export const Menu: any;
  export const MenuItem: any;
  export const dialog: any;
  export const shell: any;
  export const screen: any;
  export const clipboard: any;
  export const nativeImage: any;
  export const webContents: any;
  export const contextBridge: any;
  
  // Global variables
  export const process: {
    resourcesPath: string;
    cwd(): string;
  };
}

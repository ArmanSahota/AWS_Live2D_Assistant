// Type definitions for electron-store
// This is a simplified declaration file to resolve TypeScript errors

declare module 'electron-store' {
  interface StoreOptions<T> {
    name?: string;
    defaults?: T;
    cwd?: string;
    encryptionKey?: string | Buffer;
    fileExtension?: string;
    clearInvalidConfig?: boolean;
    serialize?: (value: T) => string;
    deserialize?: (value: string) => T;
  }

  class Store<T = any> {
    constructor(options?: StoreOptions<T>);
    get<K extends keyof T>(key: K): T[K];
    get(key: string): any;
    get(): T;
    set<K extends keyof T>(key: K, value: T[K]): void;
    set(key: string, value: any): void;
    set(object: Partial<T>): void;
    has<K extends keyof T>(key: K): boolean;
    has(key: string): boolean;
    delete<K extends keyof T>(key: K): void;
    delete(key: string): void;
    clear(): void;
    onDidChange<K extends keyof T>(key: K, callback: (newValue: T[K], oldValue: T[K]) => void): () => void;
    onDidChange(key: string, callback: (newValue: any, oldValue: any) => void): () => void;
    onDidAnyChange(callback: (newValue: T, oldValue: T) => void): () => void;
    size: number;
    store: T;
    path: string;
  }

  export = Store;
}

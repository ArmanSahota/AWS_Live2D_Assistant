/**
 * Type declarations for electron-store
 */

declare module 'electron-store' {
  interface StoreOptions<T> {
    name?: string;
    cwd?: string;
    defaults?: T;
    schema?: any;
    watch?: boolean;
    clearInvalidConfig?: boolean;
    migrations?: any;
    serialize?: (data: T) => string;
    deserialize?: (text: string) => T;
    fileExtension?: string;
    accessPropertiesByDotNotation?: boolean;
    encryptionKey?: string | Buffer;
  }

  class Store<T = any> {
    constructor(options?: StoreOptions<T>);
    get<K extends keyof T>(key: K): T[K];
    get<K extends keyof T, D>(key: K, defaultValue: D): T[K] | D;
    get(key: string): any;
    get(key: string, defaultValue: any): any;
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

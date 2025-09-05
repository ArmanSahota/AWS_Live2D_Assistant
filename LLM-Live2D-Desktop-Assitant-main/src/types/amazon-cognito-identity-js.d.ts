/**
 * Type definitions for amazon-cognito-identity-js
 * 
 * This file provides basic type definitions for the amazon-cognito-identity-js package.
 */

declare module 'amazon-cognito-identity-js' {
  export interface ICognitoUserPoolData {
    UserPoolId: string;
    ClientId: string;
    endpoint?: string;
    AdvancedSecurityDataCollectionFlag?: boolean;
  }

  export interface ICognitoUserData {
    Username: string;
    Pool: CognitoUserPool;
    Storage?: ICognitoStorage;
  }

  export interface ICognitoStorage {
    getItem(key: string): string;
    setItem(key: string, value: string): void;
    removeItem(key: string): void;
    clear(): void;
  }

  export interface IAuthenticationDetailsData {
    Username: string;
    Password?: string;
    ValidationData?: { [key: string]: any };
    ClientMetadata?: { [key: string]: string };
  }

  export class AuthenticationDetails {
    constructor(data: IAuthenticationDetailsData);
    getUsername(): string;
    getPassword(): string;
    getValidationData(): any[];
  }

  export class CognitoUserPool {
    constructor(data: ICognitoUserPoolData);
    getUserPoolId(): string;
    getClientId(): string;
    signUp(
      username: string,
      password: string,
      userAttributes: any[],
      validationData: any[],
      callback: (err: Error | null, result: any) => void
    ): void;
    getCurrentUser(): CognitoUser | null;
  }

  export class CognitoUser {
    constructor(data: ICognitoUserData);
    getUsername(): string;
    getAuthenticationFlowType(): string;
    setAuthenticationFlowType(authenticationFlowType: string): void;
    getSession(
      callback: (err: Error | null, session: CognitoUserSession | null) => void
    ): void;
    refreshSession(
      refreshToken: CognitoRefreshToken,
      callback: (err: Error | null, session: CognitoUserSession | null) => void
    ): void;
    authenticateUser(
      authenticationDetails: AuthenticationDetails,
      callbacks: {
        onSuccess: (session: CognitoUserSession) => void;
        onFailure: (err: any) => void;
        newPasswordRequired?: (userAttributes: any, requiredAttributes: any) => void;
        mfaRequired?: (challengeName: any, challengeParameters: any) => void;
        totpRequired?: (challengeName: any, challengeParameters: any) => void;
        customChallenge?: (challengeParameters: any) => void;
        mfaSetup?: (challengeName: any, challengeParameters: any) => void;
        selectMFAType?: (challengeName: any, challengeParameters: any) => void;
      }
    ): void;
    signOut(): void;
    globalSignOut(callbacks: { onSuccess: () => void; onFailure: (err: Error) => void }): void;
    confirmRegistration(
      code: string,
      forceAliasCreation: boolean,
      callback: (err: Error | null, result: any) => void
    ): void;
    sendCustomChallengeAnswer(
      answerChallenge: any,
      callback: {
        onSuccess: (session: CognitoUserSession) => void;
        onFailure: (err: Error) => void;
      }
    ): void;
    resendConfirmationCode(callback: (err: Error | null, result: any) => void): void;
    changePassword(
      oldPassword: string,
      newPassword: string,
      callback: (err: Error | null, result: any) => void
    ): void;
    forgotPassword(callbacks: {
      onSuccess: (data: any) => void;
      onFailure: (err: Error) => void;
      inputVerificationCode?: (data: any) => void;
    }): void;
    confirmPassword(
      verificationCode: string,
      newPassword: string,
      callbacks: { onSuccess: () => void; onFailure: (err: Error) => void }
    ): void;
    setDeviceStatusRemembered(callbacks: {
      onSuccess: (success: string) => void;
      onFailure: (err: any) => void;
    }): void;
    setDeviceStatusNotRemembered(callbacks: {
      onSuccess: (success: string) => void;
      onFailure: (err: any) => void;
    }): void;
    getDevice(callbacks: {
      onSuccess: (success: string) => void;
      onFailure: (err: Error) => void;
    }): void;
    forgetDevice(callbacks: {
      onSuccess: (success: string) => void;
      onFailure: (err: Error) => void;
    }): void;
    forgetSpecificDevice(
      deviceKey: string,
      callbacks: { onSuccess: (success: string) => void; onFailure: (err: Error) => void }
    ): void;
    sendMFACode(
      confirmationCode: string,
      callbacks: { onSuccess: (session: CognitoUserSession) => void; onFailure: (err: Error) => void },
      mfaType?: string
    ): void;
    listDevices(
      limit: number,
      paginationToken: string | null,
      callbacks: {
        onSuccess: (data: any) => void;
        onFailure: (err: Error) => void;
      }
    ): void;
    completeNewPasswordChallenge(
      newPassword: string,
      requiredAttributeData: any,
      callbacks: {
        onSuccess: (session: CognitoUserSession) => void;
        onFailure: (err: Error) => void;
        mfaRequired?: (challengeName: any, challengeParameters: any) => void;
        customChallenge?: (challengeParameters: any) => void;
      }
    ): void;
  }

  export class CognitoUserSession {
    constructor(data: { IdToken: CognitoIdToken; RefreshToken: CognitoRefreshToken; AccessToken: CognitoAccessToken; ClockDrift?: number });
    getIdToken(): CognitoIdToken;
    getRefreshToken(): CognitoRefreshToken;
    getAccessToken(): CognitoAccessToken;
    isValid(): boolean;
  }

  export class CognitoIdToken {
    constructor(data: { IdToken: string });
    getJwtToken(): string;
    getExpiration(): number;
  }

  export class CognitoRefreshToken {
    constructor(data: { RefreshToken: string });
    getToken(): string;
  }

  export class CognitoAccessToken {
    constructor(data: { AccessToken: string });
    getJwtToken(): string;
    getExpiration(): number;
  }
}

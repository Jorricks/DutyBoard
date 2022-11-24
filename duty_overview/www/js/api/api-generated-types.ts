/* eslint-disable */
/* tslint:disable */
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

/** CurrentSchedule */
export interface CurrentSchedule {
  /** Calendars */
  calendars: Calendar[];
  /** Persons */
  persons: Record<string, Person>;
}

/** HTTPValidationError */
export interface HTTPValidationError {
  /** Detail */
  detail?: ValidationError[];
}

/** ValidationError */
export interface ValidationError {
  /** Location */
  loc: any[];
  /** Message */
  msg: string;
  /** Error Type */
  type: string;
}

/** Calendar */
export interface Calendar {
  /** Uid */
  uid: string;
  /** Name */
  name: string;
  /** Description */
  description: string;
  /** Category */
  category: string;
  /** Order */
  order: number;
  /** Last Update */
  lastUpdate: string;
  /** Error Msg */
  errorMsg: string;
  /** Sync */
  sync: boolean;
  /** Events */
  events: Events[];
}

/** Events */
export interface Events {
  /** Start Event */
  startEvent: string;
  /** End Event */
  endEvent: string;
  /** Person Uid */
  personUid: number;
}

/** Person */
export interface Person {
  /** Ldap */
  ldap: string;
  /** Email */
  email: string;
  /** Extra Attributes */
  extraAttributes: object;
  /** Last Update */
  lastUpdate: string;
  /** Error Msg */
  errorMsg: string;
  /** Sync */
  sync: boolean;
}

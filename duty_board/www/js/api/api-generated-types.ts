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
  config: Config;
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

/** PersonResponse */
export interface PersonResponse {
  /** Uid */
  uid: string;
  /** Username */
  username?: string;
  /** Email */
  email?: string;
  /** Img Filename */
  imgFilename?: string;
  /** Extra Attributes */
  extraAttributes: ExtraInfoOnPerson[];
  /** Last Update */
  lastUpdate: string;
  /** Error Msg */
  errorMsg: string;
  /** Sync */
  sync: boolean;
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

/** Config */
export interface Config {
  /** Timezone */
  timezone: string;
  /** Text Color */
  textColor: string;
  /** Background Color */
  backgroundColor: string;
  /** Categories */
  categories: string[];
  /** Git Repository Url */
  gitRepositoryUrl?: string;
  /** Enable Admin Button */
  enableAdminButton: boolean;
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

/** ExtraInfoOnPerson */
export interface ExtraInfoOnPerson {
  /** Information */
  information: string;
  /** Icon */
  icon: string;
  /** Icon Color */
  iconColor: string;
  /** Url */
  url?: string;
}

/** Person */
export interface Person {
  /** Uid */
  uid: number;
  /** Username */
  username?: string;
  /** Email */
  email?: string;
  /** Img Filename */
  imgFilename?: string;
  /** Extra Attributes */
  extraAttributes: object;
  /** Last Update */
  lastUpdate: string;
  /** Error Msg */
  errorMsg: string;
  /** Sync */
  sync: boolean;
}

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
  persons: Person[];
}

/** _Calendar */
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
  /**
   * Last Update Utc
   * @format date-time
   */
  last_update_utc: string;
  /** Error Msg */
  error_msg: string;
  /** Sync */
  sync: boolean;
  /** Events */
  events: Events[];
}

/** _Events */
export interface Events {
  /**
   * Start Event Utc
   * @format date-time
   */
  start_event_utc: string;
  /**
   * End Event Utc
   * @format date-time
   */
  end_event_utc: string;
  /** Person Uid */
  person_uid: number;
}

/** _Person */
export interface Person {
  /** Uid */
  uid: number;
  /** Ldap */
  ldap: string;
  /** Email */
  email: string;
  /** Extra Attributes */
  extra_attributes: object;
  /**
   * Last Update Utc
   * @format date-time
   */
  last_update_utc: string;
  /** Error Msg */
  error_msg: string;
  /** Sync */
  sync: boolean;
}

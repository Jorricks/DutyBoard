import {
  Box,
  Button,
  Text,
  Popover,
  PopoverContent,
  PopoverHeader,
  PopoverCloseButton,
  PopoverBody,
  PopoverFooter,
  Portal,
  PopoverTrigger
} from "@chakra-ui/react";
import * as React from "react";
import { Events, ExtraInfoOnPerson, Person } from "../api/api-generated-types";
import { FaInfoCircle } from "react-icons/fa";
import DynamicFAIcon from "./dynamicFAIcon";
import useGetPerson from "../api/useGetPerson";

const ExtraInfoComponent = ({ information, icon, iconColor, url }: ExtraInfoOnPerson) => {
  //@Jorrick ToDo add URL to the equation
  return (
    <Box p={2} style={{ display: "flex", alignItems: "center" }}>
      <DynamicFAIcon icon={icon} color={iconColor} style={{ display: "inline-block" }} />
      <Text style={{ display: "inline-block", marginLeft: "10px" }}>{information}</Text>
    </Box>
  );
};

const LazyLoadingPopoverContent = ({ personUid }: { personUid: number }) => {
  const { data: apiPerson } = useGetPerson({ personUid });

  return (
    <>
      <PopoverHeader>{apiPerson ? apiPerson.ldap ?? apiPerson.email : "unknown"}</PopoverHeader>
      <PopoverCloseButton />
      <PopoverBody>
        {apiPerson?.extraAttributes.map((extraAttribute: ExtraInfoOnPerson, index) => (
          <ExtraInfoComponent {...extraAttribute} key={index} />
        ))}
      </PopoverBody>
      <PopoverFooter>
        Last updated: {apiPerson?.lastUpdate}
        <br />
        Sync enabled: {apiPerson?.sync ? "True" : "False"}
      </PopoverFooter>
    </>
  );
};

const PersonComponent = ({ person }: { person: Person }) => {
  const initRef = React.useRef();

  return (
    <>
      {person == undefined ? (
        "Unknown error.."
      ) : (
        <Popover placement="left" initialFocusRef={initRef} isLazy lazyBehavior='keepMounted'>
          {({ isOpen, onClose }) => (
            <>
              <PopoverTrigger>
                <Box>
                  <Text style={{ display: "inline-block" }}>{person.ldap ?? person.email}</Text>
                  <Text style={{ display: "inline-block" }}>
                    <FaInfoCircle />
                  </Text>
                </Box>
              </PopoverTrigger>
              <Portal>
                <PopoverContent>
                    <LazyLoadingPopoverContent personUid={person.uid} />
                </PopoverContent>
              </Portal>
            </>
          )}
        </Popover>
      )}
    </>
  );
};

export default PersonComponent;

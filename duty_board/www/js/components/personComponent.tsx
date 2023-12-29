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
import { ExtraInfoOnPerson, PersonEssentials, PersonResponse } from "../api/api-generated-types";
import { FaInfoCircle } from "react-icons/fa";
import DynamicFAIcon from "./dynamicFAIcon";
import useGetPerson from "../api/useGetPerson";

export interface DrawInfoOnPerson {
  information: string;
  icon: string;
  iconColor: string;
}


const ExtraInfoComponent = ({ information, icon, iconColor }: DrawInfoOnPerson) => {
  return (
    <Box p={2} style={{ display: "flex", alignItems: "center" }}>
      <DynamicFAIcon icon={icon} color={iconColor} style={{ display: "inline-block" }} />
      <Text style={{ display: "inline-block", marginLeft: "10px" }}>{information}</Text>
    </Box>
  );
};

const URLExtraInfoComponent = ({ information, icon, iconColor, url }: ExtraInfoOnPerson) => {
  return (
    <>
      {url ?
        <a href={url} target="_blank">
          <ExtraInfoComponent information={information} icon={icon} iconColor={iconColor}/>
        </a>
        : <ExtraInfoComponent information={information} icon={icon} iconColor={iconColor}/>
      }
    </>
  );
};

const PersonImage = ({person}: {person: PersonResponse}) => {
  {/* Inspiration from https://www.webfx.com/blog/web-design/circular-images-css/. Thanks William Craig! */}
  return (
    <div>
      {person.imgHeight != null && person.imgWidth != null && person.imgWidth > person.imgHeight
        ? <div className="circular--landscape">
            <img src={import.meta.env.VITE_API_ADDRESS + "person_img/" + person.imgFilename} alt={"Profile picture"}/>
          </div>
        : <div className="circular--portrait">
            <img src={import.meta.env.VITE_API_ADDRESS + "person_img/" + person.imgFilename} alt={"Profile picture"}/>
          </div>
      }
    </div>
  )
}

const LazyLoadingPopoverContent = ({ personUid }: { personUid: number }) => {
  const { data: apiPerson } = useGetPerson({ personUid });

  return (
    <>
      <PopoverHeader mt="5px" pl="20px" pb="10px" style={{fontWeight: "bold", fontSize: "20px"}}>
          {apiPerson ? apiPerson.username ?? apiPerson.email : "unknown"}
      </PopoverHeader>
      <PopoverCloseButton pt={"22px"} pr={"22px"} fontSize={"12px"}/>
      <PopoverBody>
        {apiPerson?.imgFilename &&
          <Box mb={"10px"} mt={"10px"}>
            <PersonImage person={apiPerson}/>
          </Box>
        }
        {apiPerson?.extraAttributes.map((extraAttribute: ExtraInfoOnPerson, index) => (
          <URLExtraInfoComponent {...extraAttribute} key={index} />
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

const capitalizeFirst = str => {
    return str.charAt(0).toUpperCase() + str.slice(1);
};

const PersonComponent = ({ person }: { person: PersonEssentials }) => {
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
                <Box style={{ cursor: "pointer" }}>
                  <Text mr="10px" style={{ display: "inline-block" }}>
                      {person.username != undefined ? capitalizeFirst(person.username) : person.email}
                  </Text>
                  <Text style={{ display: "inline-block", verticalAlign: "middle", fontSize: "20px" }}>
                    <FaInfoCircle />
                  </Text>
                </Box>
              </PopoverTrigger>
              <Portal>
                <PopoverContent backgroundColor={"#F5F5F5"}>
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

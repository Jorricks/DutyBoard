import {Box, PopoverBody, PopoverCloseButton, PopoverFooter, PopoverHeader, Text} from "@chakra-ui/react";
import DynamicFAIcon from "./dynamicFAIcon";
import {ExtraInfoOnPerson, PersonResponse} from "../api/api-generated-types";
import useGetPerson from "../api/useGetPerson";
import * as React from "react";

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
            <img src={import.meta.env.VITE_API_ADDRESS + "person_img/" + person.imgFilename} alt={person.username}/>
          </div>
        : <div className="circular--portrait">
            <img src={import.meta.env.VITE_API_ADDRESS + "person_img/" + person.imgFilename} alt={person.username}/>
          </div>
      }
    </div>
  )
}

const PersonLazyLoading = ({ personUid }: { personUid: number }) => {
  const { data: apiPerson } = useGetPerson({ personUid });

  return (
    <>
      <PopoverHeader mt="5px" pl="20px" pb="10px" style={{fontWeight: "bold", fontSize: "20px"}}>
          {apiPerson?.username || apiPerson?.email || "unknown"}
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

export default PersonLazyLoading;
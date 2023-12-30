import {
  Box,
  Text,
  Popover,
  PopoverContent,
  Portal,
  PopoverTrigger
} from "@chakra-ui/react";
import * as React from "react";
import { PersonEssentials } from "../api/api-generated-types";
import { FaInfoCircle } from "react-icons/fa";
import PersonLazyLoading from './personLazyLoading';


const capitalizeFirst = str => {
    return str.charAt(0).toUpperCase() + str.slice(1);
};

const PersonComponent = ({ person }: { person: PersonEssentials }) => {
  const initRef = React.useRef();

  return (
    <article>
      {person === undefined ? (
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
                    <PersonLazyLoading personUid={person.uid} />
                </PopoverContent>
              </Portal>
            </>
          )}
        </Popover>
      )}
    </article>
  );
};

export default PersonComponent;

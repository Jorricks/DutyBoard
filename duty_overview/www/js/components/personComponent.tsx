import { Box, Button, Text, Popover, PopoverContent, PopoverHeader, PopoverCloseButton, PopoverBody, PopoverFooter, Portal, PopoverTrigger } from "@chakra-ui/react";
import * as React from "react";
import {Person} from "../api/api-generated-types";
import {FaInfoCircle} from "react-icons/fa";
import DynamicFAIcon from "./dynamicFAIcon";


const PersonComponent = ({
  person
}: {person: Person}) => {
  const initRef = React.useRef()
  return (
    <>
    {person == undefined
      ? "Unknown error.."
      :
      <Popover placement='left' initialFocusRef={initRef}>
        {({isOpen, onClose}) => (
          <>
            <PopoverTrigger>
              <Box>
                <Text style={{display: "inline-block"}}>{person.ldap ?? person.email}</Text>
                <Text style={{display: "inline-block"}}><FaInfoCircle/></Text>
              </Box>
            </PopoverTrigger>
            <Portal>
              <PopoverContent>
                <PopoverHeader>{person ? (person.ldap ?? person.email) : "unknown"}</PopoverHeader>
                <PopoverCloseButton/>
                <PopoverBody>
                  <Box>
                    Hello. Nice to meet you! This is the body of the popover
                    <DynamicFAIcon icon={"Fa500Px"} size="2em" color="black"/>
                  </Box>
                  <Button
                    mt={4}
                    colorScheme='blue'
                    onClick={onClose}
                    ref={initRef}
                  >
                    Close
                  </Button>
                </PopoverBody>
                <PopoverFooter>This is the footer</PopoverFooter>
              </PopoverContent>
            </Portal>
          </>
        )}
      </Popover>
    }
    </>
  )
}

export default PersonComponent;

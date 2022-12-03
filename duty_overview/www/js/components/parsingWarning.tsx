import { Box, Heading } from "@chakra-ui/react";
import { IoWarning } from '@react-icons/all-files/io5/IoWarning';


const ParsingWarning = ({
  warningMessage
}: {warningMessage: string}) => {
  return (
    <Box textAlign="center" py={4} px={4}>
      <Heading as="h2" size="xl" color={'orange.300'} textAlign={'center'}>
        <IoWarning style={{marginLeft: "auto", marginRight: "auto"}}/>
      </Heading>
      <Heading as="h4" size="l" mt={6} mb={2} style={{whiteSpace: "pre-line"}}>
        {warningMessage}
      </Heading>
    </Box>
  );
}

export default ParsingWarning;
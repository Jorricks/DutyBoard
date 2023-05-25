import {Box, Divider, HStack, Text, useDisclosure} from "@chakra-ui/react";
import {useGetSchedule} from "../api";
import SingleCalendar from "./singleCalendar";

export default function AnnouncementBar() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const {
    data: { config },
    isLoading
  } = useGetSchedule();

  return (
    <>
      <Box bg={config.announcementBackgroundColor} color={config.announcementTextColor} px={4} fontWeight={700}>
        {config.announcements.map((announcement: string, index) => (
          <HStack spacing={8} alignItems={"center"} key={index} justifyContent={"center"}>
            <Text padding={"20px"}>{announcement}</Text>
          </HStack>
          ))}
      </Box>
    </>
  );
}

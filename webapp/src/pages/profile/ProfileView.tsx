import { PageWrapper } from '../../shared/ui';
import { 
  ProfileCard, 
  SettingsTile, 
  AboutTile 
} from './components';

export const ProfileView = () => {
  return (
    <PageWrapper className="pb-4 -mx-2">
      <ProfileCard />

      <div className="grid grid-cols-2 gap-3 mt-3">
        <SettingsTile />
        <AboutTile />
      </div>
    </PageWrapper>
  );
};

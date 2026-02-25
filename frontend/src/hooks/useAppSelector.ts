import { useSelector } from 'react-redux';
import type { RootState } from '../store';

export const useAppSelector = <TSelected = unknown>(
  selector: (state: RootState) => TSelected
): TSelected => useSelector(selector);

import { User } from './store';
import * as actions from './actions';
export type Action = actions.All;

export function user(state: User = new User(''), action: Action): any {
    
	switch (action.type) {
		case actions.LOGIN:
			return new User(action.payload);

		case actions.LOGOUT:
			return new User('');

		default:
			return state;
	}
}
